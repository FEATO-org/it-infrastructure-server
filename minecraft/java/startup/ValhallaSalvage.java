import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.*;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.nio.file.*;
import java.nio.file.attribute.PosixFilePermission;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.ZipFile;

/** One-shot pre-start correction; uses Jackson already shipped with mc-image-helper. */
class ValhallaSalvage {
    static final String SHA256 = "a3e94b75cf3d050769bba63dcf1a10df1db0b286c28cc2e11a2ff85acba403fc";
    static final List<String> FILES = List.of("grid_recipes.json", "grid_recipes_1_21_9+.json",
            "grid_recipes_26_1+.json", "grid_recipes_1_21_11+.json");
    static final ObjectMapper JSON = new ObjectMapper()
            .enable(JsonParser.Feature.STRICT_DUPLICATE_DETECTION)
            .enable(DeserializationFeature.FAIL_ON_TRAILING_TOKENS)
            .enable(DeserializationFeature.USE_BIG_DECIMAL_FOR_FLOATS)
            .enable(DeserializationFeature.USE_BIG_INTEGER_FOR_INTS);
    record Update(Path path, byte[] before, byte[] after, int inspected, int changed,
                  int unchanged, int skipped) {}

    static JsonNode parse(byte[] bytes) throws Exception {
        JsonNode tree = JSON.readTree(bytes);
        if (tree == null || !tree.isArray()) throw new IllegalArgumentException("expected recipe array");
        Set<String> names = new HashSet<>();
        for (JsonNode r : tree) {
            if (!r.isObject() || !r.path("name").isTextual() || !names.add(r.path("name").asText()))
                throw new IllegalArgumentException("invalid or duplicate recipe name");
        }
        return tree;
    }

    // Recipe keys, tinker layout and ingredient choices identify the official recipe.
    // ItemStack serialization can change when Bukkit upgrades it; never deserialize it here.
    static boolean sameIdentity(JsonNode recipe, JsonNode official) {
        for (String key : List.of("shapedKey", "shapelessKey", "tinker", "tinkerGridIndex",
                "toolIndex", "shapeless")) {
            if (!Objects.equals(recipe.get(key), official.get(key))) return false;
        }
        JsonNode items = recipe.path("items"), defaults = official.path("items");
        if (!items.isObject() || items.size() != defaults.size()) return false;
        for (Iterator<String> it = defaults.fieldNames(); it.hasNext();) {
            String slot = it.next();
            if (!Objects.equals(items.path(slot).get("option"), defaults.path(slot).get("option"))) return false;
        }
        return true;
    }

    static void run(Path plugins) throws Exception {
        // Do not use a staged updater or guess a newly released plugin's schema.
        Path jar;
        try (var stream = Files.list(plugins)) {
            List<Path> jars = stream.filter(p -> p.getFileName().toString().matches("ValhallaMMO.*\\.jar")).toList();
            if (jars.size() != 1) throw new IllegalArgumentException("expected exactly one installed ValhallaMMO JAR");
            jar = jars.getFirst();
        }
        String digest = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(jar)));
        if (!SHA256.equals(digest)) throw new IllegalArgumentException("unreviewed ValhallaMMO JAR hash; review before update");
        Path updater = plugins.resolve("update");
        if (Files.isDirectory(updater)) {
            try (var stream = Files.list(updater)) {
                if (stream.anyMatch(p -> p.getFileName().toString().matches("(?i).*valhallammo.*\\.jar")))
                    throw new IllegalArgumentException("staged ValhallaMMO updater JAR; review before start");
            }
        }
        Map<String, List<JsonNode>> official = new HashMap<>();
        Map<String, byte[]> seeds = new HashMap<>();
        try (ZipFile zip = new ZipFile(jar.toFile())) {
            for (String file : FILES) {
                try (var input = zip.getInputStream(zip.getEntry("recipes/" + file))) {
                    byte[] bytes = input.readAllBytes();
                    seeds.put(file, bytes);
                    for (JsonNode r : parse(bytes)) {
                        String name = r.path("name").asText();
                        if (name.startsWith("salvage_")) official.computeIfAbsent(name, k -> new ArrayList<>()).add(r);
                    }
                }
            }
        }
        Path folder = plugins.resolve("ValhallaMMO/recipes");
        if (Files.isSymbolicLink(plugins.resolve("ValhallaMMO")) || Files.isSymbolicLink(folder))
            throw new IllegalArgumentException("symlink recipe directory refused");
        List<Update> updates = new ArrayList<>();
        // Validate every file before writing any. Seed only files enabled on the pinned Paper 26.2.
        for (String file : FILES) {
            Path path = folder.resolve(file);
            if (Files.isSymbolicLink(path)) throw new IllegalArgumentException("symlink recipe file refused: " + file);
            boolean exists = Files.exists(path);
            if (!exists && file.equals("grid_recipes_1_21_11+.json")) {
                System.out.println("[ValhallaSalvage] file=" + path + " inspected=0 changed=0 unchanged=0 skipped=0 reason=inactive-version-missing");
                continue;
            }
            System.out.println("[ValhallaSalvage] validating file=" + path + " source=" + (exists ? "volume" : "official-JAR-seed"));
            byte[] before = exists ? Files.readAllBytes(path) : null;
            JsonNode recipes = parse(exists ? before : seeds.get(file));
            int inspected = 0, changed = 0, unchanged = 0, skipped = 0;
            for (JsonNode recipe : recipes) {
                String name = recipe.path("name").asText();
                if (!name.startsWith("salvage_")) continue;
                inspected++;
                List<JsonNode> candidates = official.getOrDefault(name, List.of());
                if (candidates.stream().noneMatch(r -> sameIdentity(recipe, r))) {
                    skipped++;
                    continue;
                }
                if (!recipe.path("requireValhallaTools").isBoolean())
                    throw new IllegalArgumentException("official salvage has non-boolean quality flag: " + file);
                if (recipe.path("requireValhallaTools").asBoolean()) {
                    ((ObjectNode) recipe).put("requireValhallaTools", false);
                    changed++;
                } else unchanged++;
            }
            byte[] after = changed == 0 && exists ? before : JSON.writerWithDefaultPrettyPrinter().writeValueAsBytes(recipes);
            updates.add(new Update(path, before, after, inspected, changed, unchanged, skipped));
        }
        for (Update update : updates) {
            Path path = update.path();
            if (update.before() == null || update.changed() > 0) {
                Files.createDirectories(folder);
                Path temp = Files.createTempFile(folder, ".salvage-", ".tmp");
                try {
                    Files.write(temp, update.after());
                    parse(Files.readAllBytes(temp));
                    Set<PosixFilePermission> mode = update.before() == null
                            ? java.nio.file.attribute.PosixFilePermissions.fromString("rw-r--r--") : Files.getPosixFilePermissions(path);
                    Files.setPosixFilePermissions(temp, mode);
                    // No non-atomic fallback: leave the original intact if the filesystem cannot support this.
                    Files.move(temp, path, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
                } finally { Files.deleteIfExists(temp); }
            }
            System.out.printf("[ValhallaSalvage] file=%s inspected=%d changed=%d unchanged=%d skipped=%d reason=%s%n",
                    path, update.inspected(), update.changed(), update.unchanged(), update.skipped(),
                    update.skipped() > 0 ? "unrecognized-identity-review-required" : "ok");
        }
    }

    public static void main(String[] args) {
        try {
            if (args.length != 1) throw new IllegalArgumentException("expected plugins directory");
            run(Path.of(args[0]));
        } catch (Exception e) {
            // Parser errors can quote input; do not print recipe contents or arbitrary names.
            String detail = e instanceof IllegalArgumentException ? e.getMessage() : "JSON validation or file operation failed (" + e.getClass().getSimpleName() + ")";
            System.err.println("[ValhallaSalvage] ERROR: " + detail);
            System.exit(1);
        }
    }
}
