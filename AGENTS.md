# AGENTS.md — Development Guidelines & Rules for EnterMedia (EME)

This document outlines mandatory architecture rules, best practices, and patterns for AI agents and developers working in this codebase.

---

## 1. Core Directives & Golden Rules

### 🚫 1. Never Create Groovy Scripts for Features or Endpoints

- **Do NOT** create random or standalone `.groovy` scripts under `services/`, `scripts/`, or web folders when asked to add a new feature, endpoint, or bug fix.
- **Do NOT** map endpoints using `<path-action name="Script.run">`.
- Existing Groovy scripts are legacy and should be converted to structured Java module actions (see `.agents/skills/convert-groovy-to-java-module/SKILL.md`). However, the ones under `events` folders are used for event handling and should be preserved as is.

### 2. Build Structured Java Modules

- Place or edit Java module classes inside the appropriate plugin's source folder: `plugins/<plugin>/code/<package>/`.
- Extend `BaseMediaModule` (or domain-specific base classes such as `TestUBaseModule`).
- Implement actions as public methods taking `WebPageRequest inReq` (e.g., `public void myAction(WebPageRequest inReq)`).

### ⚙️ 3. Register Modules in `plugin.xml`

- Every new or modified Java module used in endpoints **must** be registered as a bean in `plugins/<plugin>/html/src/plugin.xml`.
- Module beans must use `scope="prototype"` and inject `moduleManager`:
  ```xml
  <bean id="MyCustomModule" class="org.entermediadb.custom.MyCustomModule" scope="prototype">
      <property name="moduleManager">
          <ref bean="moduleManager" />
      </property>
  </bean>
  ```

### 🔗 4. Wire Actions via `.xconf` Files

- Reference registered Java module actions in endpoint `.xconf` files using `<path-action name="BeanName.methodName"/>` or `<page-action name="BeanName.methodName"/>`.
  ```xml
  <page>
      <path-action name="MyCustomModule.myAction"/>
      <permission name="view"><userprofile property="view_permission" equals="true"/></permission>
  </page>
  ```

### ⚡ 5. No Manual Compilation Needed

- **Do NOT** run manual `javac` compilation commands in terminal.
- The IDE runtime and launcher build Java source files automatically into the output build/bin directory on save or restart.

---

## 2. Standard Endpoint & Module Workflow

Follow this 4-step sequence when adding or updating backend endpoints:

```
[Request] ──► [endpoint.xconf] ──► [<path-action name="BeanName.action"/>] ──► [endpoint.json / template]
                                               │
                                               ▼
                                  [plugin.xml Spring Bean]
                                               │
                                               ▼
                              [Java: Class extends BaseMediaModule]
```

### Step 1: Create or Update the Java Module

Location: `plugins/<plugin>/code/<package>/<ModuleName>.java`

```java
package org.entermediadb.custom;

import org.entermediadb.asset.MediaArchive;
import org.entermediadb.asset.modules.BaseMediaModule;
import org.json.simple.JSONObject;
import org.openedit.Data;
import org.openedit.WebPageRequest;
import org.openedit.data.Searcher;

public class MyCustomModule extends BaseMediaModule
{
    public void executeAction(WebPageRequest inReq)
    {
        MediaArchive archive = getMediaArchive(inReq);
        String id = inReq.getRequestParameter("id");

        if (id == null || id.trim().isEmpty())
        {
            fail(inReq, 400, "Missing required parameter: id");
            return;
        }

        Searcher searcher = archive.getSearcher("mydata");
        Data data = (Data) searcher.searchById(id);

        JSONObject response = new JSONObject();
        response.put("ok", Boolean.TRUE);
        response.put("data", data != null ? data.getName() : null);

        reply(inReq, response);
    }

    protected void reply(WebPageRequest inReq, Object responseObj)
    {
        if (responseObj != null)
        {
            inReq.putPageValue("json", responseObj.toString());
        }
    }

    protected void fail(WebPageRequest inReq, int statusCode, String message)
    {
        if (inReq.getResponse() != null)
        {
            inReq.getResponse().setStatus(statusCode);
        }
        JSONObject err = new JSONObject();
        err.put("ok", Boolean.FALSE);
        err.put("error", message);
        reply(inReq, err);
        inReq.setCancelActions(true);
    }
}
```

### Step 2: Register Bean in `plugin.xml`

Location: `plugins/<plugin>/html/src/plugin.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans projectname="myplugin" depends="finder">
    <bean id="MyCustomModule" class="org.entermediadb.custom.MyCustomModule" scope="prototype">
        <property name="moduleManager">
            <ref bean="moduleManager" />
        </property>
    </bean>
</beans>
```

### Step 3: Configure the Endpoint `.xconf`

Location: `plugins/<plugin>/html/services/<path>/<action>.xconf`

```xml
<page>
    <path-action name="MyCustomModule.executeAction"/>
    <permission name="view"><userprofile property="api_access" equals="true"/></permission>
</page>
```

### Step 4: Add Response Template (JSON APIs)

Location: `plugins/<plugin>/html/services/<path>/<action>.json`

```velocity
$json
```

---

## 3. Common Java EME Code Patterns

| Task                         | Pattern                                                                                 |
| ---------------------------- | --------------------------------------------------------------------------------------- |
| **Get MediaArchive**         | `MediaArchive archive = getMediaArchive(inReq);`                                        |
| **Get Request Parameter**    | `String val = inReq.getRequestParameter("paramName");`                                  |
| **Get Current User**         | `User user = inReq.getUser();`                                                          |
| **Get Current User Profile** | `UserProfile profile = inReq.getUserProfile();`                                         |
| **Check Permissions**        | `if (profile != null && profile.hasPermission("perm_name")) { ... }`                    |
| **Get Searcher**             | `Searcher s = archive.getSearcher("tablename");`                                        |
| **Search by ID**             | `Data record = (Data) s.searchById(id);`                                                |
| **Query Data**               | `HitTracker hits = archive.query("tablename").exact("field", value).search();`          |
| **Create & Save Data**       | `Data d = s.createNewData(); d.setValue("field", val); s.saveData(d, inReq.getUser());` |
| **Parse Stored Date**        | `DateStorageUtil.getStorageUtil().parseFromObject(record.getValue("datefield"));`       |
| **Halt Pipeline on Error**   | `inReq.setCancelActions(true); inReq.getResponse().setStatus(400);`                     |

---

## 4. Codebase & Plugin Layout Reference

- `plugins/<plugin>/code/`: Java source packages (`org.entermediadb...`, `tech.genailabs...`).
- `plugins/<plugin>/html/src/plugin.xml`: Spring prototype bean definitions.
- `plugins/<plugin>/html/services/`: REST / JSON service endpoints and `.xconf` descriptors.
- `plugins/catalog/html/data/lists/`: System configurations, endpoints, and catalog definitions.
- `plugins/finder/`: Core media library backend modules and UI components.
- `plugins/system/`: Base web request handling, security, and authentication.

---

## 5. Decision Tree for Changes

1. **Adding/Editing HTML/Velocity Templates (`.html`, `.json`)**:
   - Changes take effect on browser refresh.
2. **Adding/Editing Endpoint Descriptors (`.xconf`)**:
   - Server page cache needs to be cleared or restarted.
   - If using `webapp/site/mediadb/` mirror, sync HTML/XCONF files from `plugins/<plugin>/html/`.
3. **Adding/Editing Java Modules (`.java`) & Spring Wiring (`plugin.xml`)**:
   - Ensure the bean is registered in `plugin.xml`.
   - Rebuild/hot-reload or restart Tomcat server.
