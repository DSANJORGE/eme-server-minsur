---
name: convert-groovy-to-java-module
description: Use this skill whenever converting Groovy scripts under services/ or scripts/ to Java module actions in EnterMedia/EME. Covers creating BaseMediaModule classes, grouping actions into domain modules, registering Spring beans in plugin.xml, and updating endpoint .xconf files. Avoids manual javac compilation as the IDE/runtime handles compilation.
---

# Convert Groovy Scripts to Java Module Actions

Converts Groovy endpoint scripts (run via `Script.run` in `.xconf` files) into structured Java module actions following the standard EnterMedia / EME architecture.

## Overview & Architecture

In EME, API endpoints are typically mapped through `.xconf` files that invoke module actions and render the output via `.json` templates (e.g. `$json`).

```
[Request] -> [endpoint.xconf] -> [<path-action name="MyModule.myAction"/>] -> [endpoint.json ($json)]
                                                 │
                                                 ▼
                                        [Spring Bean: plugin.xml]
                                                 │
                                                 ▼
                                     [Java: MyModule extends BaseMediaModule]
```

---

## Step 1: Create Shared Base Module (if not already present)

When converting multiple scripts, encapsulate shared boilerplate (JSON replies, error handling, audit logging, snapshots) into a base module:

```java
package tech.genailabs.tutor; // adjust package as appropriate

import java.util.Collection;
import java.util.Date;
import java.util.Map;
import org.entermediadb.asset.MediaArchive;
import org.entermediadb.asset.modules.BaseMediaModule;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;
import org.openedit.Data;
import org.openedit.WebPageRequest;
import org.openedit.data.Searcher;
import org.openedit.users.User;

public class TestUBaseModule extends BaseMediaModule
{
	@Override
	public MediaArchive getMediaArchive(WebPageRequest inReq)
	{
		MediaArchive archive = super.getMediaArchive(inReq);
		if (archive == null)
		{
			archive = (MediaArchive) inReq.getPageValue("mediaarchive");
		}
		return archive;
	}

	public void reply(WebPageRequest inReq, Object responseObj)
	{
		if (responseObj instanceof JSONObject)
		{
			inReq.putPageValue("json", ((JSONObject) responseObj).toJSONString());
		}
		else if (responseObj instanceof JSONArray)
		{
			inReq.putPageValue("json", ((JSONArray) responseObj).toJSONString());
		}
		else if (responseObj instanceof Map)
		{
			inReq.putPageValue("json", JSONObject.toJSONString((Map<?, ?>) responseObj));
		}
		else if (responseObj instanceof String)
		{
			inReq.putPageValue("json", (String) responseObj);
		}
		else if (responseObj != null)
		{
			inReq.putPageValue("json", JSONValue.toJSONString(responseObj));
		}
	}

	public void fail(WebPageRequest inReq, int code, String msg)
	{
		if (inReq.getResponse() != null)
		{
			inReq.getResponse().setStatus(code);
		}
		JSONObject err = new JSONObject();
		err.put("ok", Boolean.FALSE);
		err.put("error", msg);
		reply(inReq, err);
		inReq.setCancelActions(true);
	}

	public void audit(WebPageRequest inReq, MediaArchive archive, String action, String targettype, String targetid, Object before, Object after)
	{
		Searcher s = archive.getSearcher("auditevent");
		Data e = s.createNewData();
		e.setValue("datecreated", new Date());
		User actor = inReq.getUser();
		e.setValue("actor", actor != null ? actor.getId() : null);
		e.setValue("action", action);
		e.setValue("targettype", targettype);
		e.setValue("targetid", targetid);
		e.setValue("before", before == null ? "" : toJsonString(before));
		e.setValue("after", after == null ? "" : toJsonString(after));
		s.saveData(e, actor);
	}

	public JSONObject snapshot(Data d, String... fields)
	{
		if (d == null) return null;
		JSONObject map = new JSONObject();
		for (String field : fields) map.put(field, d.get(field));
		return map;
	}

	protected String toJsonString(Object obj)
	{
		if (obj == null) return "";
		if (obj instanceof JSONObject) return ((JSONObject) obj).toJSONString();
		if (obj instanceof JSONArray) return ((JSONArray) obj).toJSONString();
		if (obj instanceof Map) return JSONObject.toJSONString((Map<?, ?>) obj);
		if (obj instanceof String) return (String) obj;
		return JSONValue.toJSONString(obj);
	}
}
```

---

## Step 2: Implement Domain Action Modules

Group related actions logically into domain-specific Java classes (e.g. `UserModule`, `TeamModule`, `AnalyticsModule`) placed in `plugins/<plugin>/code/<package>/`.

```java
package tech.genailabs.tutor;

import org.entermediadb.asset.MediaArchive;
import org.json.simple.JSONObject;
import org.openedit.Data;
import org.openedit.WebPageRequest;
import org.openedit.data.Searcher;

public class TestUTeamModule extends TestUBaseModule
{
	public void saveTeam(WebPageRequest inReq)
	{
		MediaArchive archive = getMediaArchive(inReq);
		String id = inReq.getRequestParameter("id");
		id = (id != null) ? id.trim().toLowerCase() : "";

		if (!id.matches("^[a-z0-9]+$"))
		{
			fail(inReq, 400, "id must be [a-z0-9]+");
			return;
		}

		Searcher teams = archive.getSearcher("team");
		Data t = (Data) teams.searchById(id);
		String[] fields = new String[] {"name", "parent", "manager", "location", "costcenter"};
		JSONObject before = snapshot(t, fields);

		if (t == null)
		{
			t = teams.createNewData();
			t.setId(id);
		}

		for (String f : fields)
		{
			String val = inReq.getRequestParameter(f);
			t.setValue(f, (val != null && !val.isEmpty()) ? val : null);
		}
		t.setValue("enabled", "true");
		teams.saveData(t, inReq.getUser());

		audit(inReq, archive, "team.save", "team", id, before, snapshot(t, fields));

		JSONObject replyObj = new JSONObject();
		replyObj.put("ok", Boolean.TRUE);
		replyObj.put("id", id);
		reply(inReq, replyObj);
	}
}
```

### Common Groovy to Java Patterns

| Groovy Construct | Java Equivalent |
|---|---|
| `context.getPageValue("mediaarchive")` | `getMediaArchive(inReq)` |
| `context.getRequestParameter("x")` | `inReq.getRequestParameter("x")` |
| `context.getUser()` / `getUserProfile()` | `inReq.getUser()` / `inReq.getUserProfile()` |
| `profile.hasPermission("perm")` | `profile != null && profile.hasPermission("perm")` |
| `archive.query("type").all().search()` | `HitTracker hits = archive.query("type").all().search();` |
| `hits.enableBulkOperations()` | `hits.enableBulkOperations();` |
| `r.getDate("datefield")` | `DateStorageUtil.getStorageUtil().parseFromObject(r.getValue("datefield"))` |
| `archive.getSearcher("type")` | `Searcher s = archive.getSearcher("type");` |
| `searcher.searchById(id)` | `(Data) searcher.searchById(id);` |
| `searcher.saveData(d, user)` | `searcher.saveData(d, inReq.getUser());` |
| `context.putPageValue("json", ...)` | `reply(inReq, resultObject)` |
| `fail(code, msg)` | `fail(inReq, code, msg)` |

---

## Step 3: Register Bean in `plugin.xml`

In `plugins/<plugin>/html/src/plugin.xml`, register each new module class as a prototype bean with `moduleManager` property injected:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans projectname="testu" depends="finder">
	<bean id="TestUUserModule" class="tech.genailabs.tutor.TestUUserModule" scope="prototype">
		<property name="moduleManager">
			<ref bean="moduleManager" />
		</property>
	</bean>
	<bean id="TestUTeamModule" class="tech.genailabs.tutor.TestUTeamModule" scope="prototype">
		<property name="moduleManager">
			<ref bean="moduleManager" />
		</property>
	</bean>
</beans>
```

---

## Step 4: Update `.xconf` Endpoints

Replace `<path-action name="Script.run">` in `.xconf` files with the registered Java bean action:

### Before (Groovy):
```xml
<page>
  <path-action name="Script.run"><script>/${applicationid}/services/testu/personas/scripts/createuser.groovy</script></path-action>
  <permission name="view"><userprofile property="personas_operate" equals="true"/></permission>
</page>
```

### After (Java Module Action):
```xml
<page>
  <path-action name="TestUUserModule.createUser"/>
  <permission name="view"><userprofile property="personas_operate" equals="true"/></permission>
</page>
```

If multiple actions need to run sequentially (e.g. computing scope before loading data):
```xml
<page>
  <path-action name="TestUTeamModule.loadScope"/>
  <path-action name="TestUUserModule.loadUsers" allowduplicates="true"/>
  <permission name="view"><userprofile property="personas_view" equals="true"/></permission>
</page>
```

---

## Step 5: Sync Endpoints (if using WebApp mirror)

If the server serves files from `webapp/site/mediadb/`, sync the `.xconf` changes from `plugins/<plugin>/html/` to `webapp/site/mediadb/` using the plugin deploy script or `rsync`:

```bash
rsync -a --exclude '.DS_Store' plugins/<plugin>/html/ webapp/site/mediadb/
```

---

## Note on Compilation

> [!NOTE]
> Manual compilation (e.g. `javac -cp ...`) is **not required** during development. The IDE and Tomcat workspace launcher build Java source files automatically into the output build/bin directory on save or restart.
