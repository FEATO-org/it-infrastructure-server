import com.fastasyncworldedit.core.limit.FaweLimit;
import com.fastasyncworldedit.core.history.changeset.BlockBagChangeSet;
import com.sk89q.worldedit.EditSession;
import com.sk89q.worldedit.WorldEdit;
import com.sk89q.worldedit.bukkit.BukkitAdapter;
import com.sk89q.worldedit.extent.inventory.BlockBag;
import com.sk89q.worldedit.math.BlockVector3;
import com.sk89q.worldedit.world.block.BlockTypes;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.PlayerInventory;
import org.bukkit.metadata.MetadataValue;
import org.bukkit.plugin.java.JavaPlugin;

import java.lang.reflect.Proxy;
import java.util.*;

/** Isolated Paper probe only. Never install in production. No commands or permissions. */
public final class FaweInventoryProbe extends JavaPlugin {
    private static final UUID PROBE_ID = UUID.fromString("c8a0255a-a550-4c0a-a23a-7c61223501fa");
    private void check(boolean ok, String label) {
        if (!ok) throw new IllegalStateException(label);
        getLogger().info("PASS " + label);
    }

    @Override public void onEnable() {
        if (!Boolean.getBoolean("feato.fawe.inventory-probe")
                || Bukkit.getWorld("fawe-test") == null) {
            getLogger().warning("Probe requires explicit JVM opt-in and isolated fawe-test world");
            Bukkit.getPluginManager().disablePlugin(this);
            return;
        }
        Bukkit.getServicesManager().load(net.luckperms.api.LuckPerms.class).getUserManager()
                .loadUser(PROBE_ID).thenRun(() -> Bukkit.getScheduler().runTaskLater(this, () -> {
            try {
                runCase("single", new int[]{64}, 10, 10, 54, 10);
                runCase("multiple", new int[]{64, 32}, 80, 80, 16, 80);
                runCase("insufficient", new int[]{5}, 10, 10, 0, 5);
                runCase("empty", new int[]{}, 10, 10, 0, 0);
                runCase("limit", new int[]{64}, 10, 3, 61, 3);
                getLogger().info("FAWE_INVENTORY_PROBE_SUCCESS");
            } catch (Throwable failure) {
                getLogger().log(java.util.logging.Level.SEVERE, "FAWE_INVENTORY_PROBE_FAILURE", failure);
            }
        }, 100L));
    }

    private void runCase(String label, int[] stacks, int requested, int max, int left, int placed) throws Exception {
        var world = Objects.requireNonNull(Bukkit.getWorld("fawe-test"));
        // Real Bukkit ItemStacks; Player/PlayerInventory are test doubles. No connected player is modified.
        ItemStack[][] contents = {new ItemStack[41]};
        for (int i = 0; i < stacks.length; i++) contents[0][i] = new ItemStack(Material.STONE_BRICKS, stacks[i]);
        PlayerInventory inventory = (PlayerInventory) Proxy.newProxyInstance(getClassLoader(),
                new Class<?>[]{PlayerInventory.class}, (proxy, method, args) -> switch (method.getName()) {
                    case "getContents" -> Arrays.stream(contents[0]).map(i -> i == null ? null : i.clone()).toArray(ItemStack[]::new);
                    case "setContents" -> { contents[0] = (ItemStack[]) args[0]; yield null; }
                    default -> throw new UnsupportedOperationException(method.getName());
                });
        UUID id = PROBE_ID;
        Map<String, List<MetadataValue>> metadata = new HashMap<>();
        Player player = (Player) Proxy.newProxyInstance(getClassLoader(), new Class<?>[]{Player.class}, (proxy, method, args) ->
                switch (method.getName()) {
                    case "getInventory" -> inventory;
                    case "getUniqueId" -> id;
                    case "getName" -> "FaweProbe";
                    case "getWorld" -> world;
                    case "getGameMode" -> GameMode.SURVIVAL;
                    case "getMetadata" -> metadata.getOrDefault((String) args[0], List.of());
                    case "setMetadata" -> { metadata.put((String) args[0], List.of((MetadataValue) args[1])); yield null; }
                    case "hasMetadata" -> metadata.containsKey((String) args[0]);
                    case "isOp", "hasPermission", "isPermissionSet" -> false;
                    case "isOnline", "isValid" -> true;
                    case "getLocale" -> "en_us";
                    case "sendMessage", "sendRawMessage" -> null;
                    case "hashCode" -> id.hashCode();
                    case "equals" -> proxy == args[0];
                    case "toString" -> "FaweProbe";
                    default -> throw new UnsupportedOperationException(method.getName());
                });
        var actor = BukkitAdapter.adapt(player);
        check(actor.getUniqueId().equals(id), label + " Bukkit Player -> Actor");
        BlockBag bag = actor.getInventoryBlockBag();
        check(bag != null, label + " Player inventory BlockBag");
        FaweLimit limit = FaweLimit.MAX.copy();
        limit.INVENTORY_MODE = 2;
        limit.MAX_CHANGES.set(max);
        int z = switch (label) { case "single" -> 0; case "multiple" -> 2; case "insufficient" -> 4; case "empty" -> 6; default -> 8; };
        for (int x = 0; x < requested; x++) world.getBlockAt(x, 150, z).setType(Material.AIR, false);
        EditSession edit = WorldEdit.getInstance().newEditSessionBuilder()
                .world(BukkitAdapter.adapt(world)).actor(actor).limit(limit).maxBlocks(max)
                .blockBag(bag).fastMode(false).changeSet(false, id).combineStages(false)
                .allowedRegionsEverywhere().checkMemory(false).build();
        check(edit.getBlockBag() == bag && edit.getChangeSet() instanceof BlockBagChangeSet,
                label + " History + BlockBag active");
        try (edit) {
            for (int x = 0; x < requested; x++) {
                try {
                    edit.setBlock(BlockVector3.at(x, 150, z), BlockTypes.STONE_BRICKS.getDefaultState());
                } catch (com.sk89q.worldedit.WorldEditException | com.fastasyncworldedit.core.internal.exception.FaweException expected) {
                    getLogger().info(label + " rejected: " + expected.getClass().getSimpleName());
                    break;
                }
            }
        } finally {
            bag.flushChanges();
        }
        int remaining = Arrays.stream(contents[0]).filter(Objects::nonNull)
                .filter(i -> i.getType() == Material.STONE_BRICKS).mapToInt(ItemStack::getAmount).sum();
        int actual = 0;
        for (int x = 0; x < requested; x++) if (world.getBlockAt(x, 150, z).getType() == Material.STONE_BRICKS) actual++;
        check(remaining == left && actual == placed, label + " remaining=" + remaining + " placed=" + actual);
        check(edit.getChangeSet().size() == placed, label + " recorded history=" + edit.getChangeSet().size());
        try (EditSession undo = WorldEdit.getInstance().newEditSessionBuilder()
                .world(BukkitAdapter.adapt(world)).actor(actor).limit(FaweLimit.MAX.copy())
                .fastMode(false).changeSet(false, id).allowedRegionsEverywhere().checkMemory(false).build()) {
            edit.undo(undo);
        }
        for (int x = 0; x < requested; x++) {
            if (world.getBlockAt(x, 150, z).getType() != Material.AIR) throw new IllegalStateException(label + " undo x=" + x);
        }
        check(true, label + " undo restored all positions");
    }
}
