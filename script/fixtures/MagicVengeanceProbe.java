// Test-only plugin for isolated Paper 26.2 / Magic 11.2.4 / ValhallaMMO 1.10.3.
// Never install on production: creates a console mage and simulated cast contexts.
import org.bukkit.plugin.java.JavaPlugin;
import com.elmakers.mine.bukkit.magic.MagicPlugin;
import com.elmakers.mine.bukkit.api.spell.MageSpell;
import com.elmakers.mine.bukkit.api.magic.VariableScope;
import com.elmakers.mine.bukkit.spell.BaseSpell;
import com.elmakers.mine.bukkit.configuration.SpellParameters;
import com.elmakers.mine.bukkit.action.CastContext;
import com.elmakers.mine.bukkit.action.builtin.ModifyVariableAction;

public class MagicVengeanceProbe extends JavaPlugin {
  public void onEnable() {
    getServer().getScheduler().runTaskLater(this, () -> {
      try { check(); getLogger().info("PROBE PASS"); }
      catch (Throwable e) { getLogger().log(java.util.logging.Level.SEVERE,"PROBE FAIL",e); }
    }, 140L);
  }
  static void require(boolean ok, String message) { if (!ok) throw new AssertionError(message); }
  void check() {
    MagicPlugin magic=(MagicPlugin)getServer().getPluginManager().getPlugin("Magic");
    require(magic.isEnabled(),"Magic enabled");
    require(getServer().getPluginManager().isPluginEnabled("ValhallaMMO"),"Valhalla enabled");
    require(getServer().getPluginManager().isPluginEnabled("DeadChest"),"DeadChest enabled");
    double[] factors={0.4,0.6,0.8};
    for(int i=0;i<3;i++) {
      String key=i==0?"vengeance":"vengeance|"+(i+1);
      var template=magic.getSpellTemplate(key);
      require(template!=null,key+" template");
      require(template.getSpellParameters().getDouble("damage")==0,key+" initial expression");
      require(template.getConfiguration().getString("earns_type").equals("valhalla_xp_magic"),key+" XP integration");
      MageSpell spell=magic.getMage(getServer().getConsoleSender()).getSpell(key);
      require(spell!=null,key+" mage spell");
      require(spell.getVariableScope("bubble")==VariableScope.CAST,key+" cast scope");
      class TestContext extends CastContext {
        TestContext() { super(spell); }
        public Double getAttribute(String name) { return name.equals("damage")?4.0:super.getAttribute(name); }
      }
      TestContext context=new TestContext();
      SpellParameters params=new SpellParameters(spell,context,template.getConfiguration().getConfigurationSection("parameters"));
      context.setWorkingParameters(params);
      ((BaseSpell)spell).initializeVariables(params);
      require(params.getParameters().contains("bubble"),key+" registered");
      require(params.getParameter("bubble")==0,key+" fresh cast");
      ModifyVariableAction action=new ModifyVariableAction();
      action.initialize(spell,params);
      action.prepare(context,params);
      for(int hit=1;hit<=3;hit++) {
        action.perform(context);
        require(params.getParameter("bubble")==4*hit,key+" accumulation "+hit);
        require(Math.abs(params.getDouble("damage")-factors[i]*4*hit)<1e-9,key+" rank multiplier");
      }
      TestContext next=new TestContext();
      SpellParameters nextParams=new SpellParameters(spell,next,template.getConfiguration().getConfigurationSection("parameters"));
      ((BaseSpell)spell).initializeVariables(nextParams);
      require(nextParams.getParameter("bubble")==0,key+" next cast reset");
      require(params.getParameter("bubble")==12,key+" prior cast isolated");
      require(!spell.getVariables().contains("bubble"),key+" no spell persistence");
      getLogger().info(key+" initial 0, three simulated damage updates, multiplier "+factors[i]+", fresh cast reset PASS");
    }
  }
}
