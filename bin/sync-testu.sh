#!/usr/bin/env bash
#
# Copies the TestU learning-engine runtime files from the plugins/testu checkout (its own repo, ignored here) into
# webapp/, which Tomcat serves: endpoint templates and descriptors, field and list definitions, plugin wiring and
# the computemastery event, and the learner/admin web bundles (app-genailabs build_learn.sh / build_admin.sh write both copies). The copies are committed, so a deploy of this repo alone carries every engine artifact.
#
# Usage (from the server root):
#   bin/sync-testu.sh           copy every listed file that differs
#   bin/sync-testu.sh --check   copy nothing; list missing or differing files and exit 1 if any
#
# Java (plugins/testu/code) is not copied: bin/compile.sh builds it into build/.

set -eu
cd "$(dirname "$0")/.."

P=plugins/testu
F=webapp/WEB-INF/data/site/catalog
# source (under plugins/testu) -> destination; a directory entry covers every file below it
MAP=(
	"data/fields/dailychallengeset.xml         $F/fields/dailychallengeset.xml"
	"data/fields/entityquestion.xml            $F/fields/entityquestion.xml"
	"data/fields/entitytopic.xml               $F/fields/entitytopic.xml"
	"data/fields/learningsession.xml           $F/fields/learningsession.xml"
	"data/fields/masterylevel.xml              $F/fields/masterylevel.xml"
	"data/fields/subtopicpolicy.xml            $F/fields/subtopicpolicy.xml"
	"data/fields/subtopicunlock.xml            $F/fields/subtopicunlock.xml"
	"data/fields/topicrequirement.xml          $F/fields/topicrequirement.xml"
	"data/fields/tutoranswer.xml               $F/fields/tutoranswer.xml"
	"data/fields/tutorexposure.xml             $F/fields/tutorexposure.xml"
	"data/fields/tutormastery.xml              $F/fields/tutormastery.xml"
	"data/fields/tutormasteryday.xml           $F/fields/tutormasteryday.xml"
	"html/services/testu/analytics/forecast.xconf webapp/site/mediadb/services/testu/analytics/forecast.xconf"
	"html/services/testu/analytics/forecast.json webapp/site/mediadb/services/testu/analytics/forecast.json"
	"html/services/testu/analytics/engagement.xconf webapp/site/mediadb/services/testu/analytics/engagement.xconf"
	"html/services/testu/analytics/engagement.json webapp/site/mediadb/services/testu/analytics/engagement.json"
	"data/fields/usageevent.xml                $F/fields/usageevent.xml"
	"data/fields/termsversion.xml              $F/fields/termsversion.xml"
	"data/fields/termsacceptance.xml           $F/fields/termsacceptance.xml"
	"data/lists/termsdecision.xml              $F/lists/termsdecision.xml"
	"data/lists/jobrole.xml                    $F/lists/jobrole.xml"
	"data/lists/masterylevel.xml               $F/lists/masterylevel.xml"
	"data/lists/questionflagreason.xml         $F/lists/questionflagreason.xml"
	"data/system/fields/user.xml               webapp/WEB-INF/data/system/fields/user.xml"
	"html/services/testu/learn                 webapp/site/mediadb/services/testu/learn"
	"html/services/testu/personas              webapp/site/mediadb/services/testu/personas"
	"html/learn                                webapp/site/mediadb/learn"
	"html/admin                                webapp/site/mediadb/admin"
	"html/src/plugin.xml                       webapp/site/mediadb/src/plugin.xml"
	"catalog/events/testu/computemastery.xconf webapp/site/catalog/events/testu/computemastery.xconf"
	"catalog/events/scripts/testu/computemastery.groovy webapp/site/catalog/events/scripts/testu/computemastery.groovy"
)

check=false
[ "${1:-}" = "--check" ] && check=true
[ -d "$P" ] || { echo "missing $P checkout" >&2; exit 1; }

drift=0
for entry in "${MAP[@]}"; do
	read -r src dst <<<"$entry"
	[ -e "$P/$src" ] || { echo "missing source $P/$src" >&2; exit 1; }
	while IFS= read -r f; do
		rel=${f#"$P/$src"}
		to="$dst$rel"
		if ! cmp -s "$f" "$to"; then
			drift=$((drift + 1))
			if $check; then
				echo "differs: $to"
			else
				mkdir -p "$(dirname "$to")"
				cp "$f" "$to"
				echo "copied:  $to"
			fi
		fi
	done < <(find "$P/$src" -type f | sort)
done

if $check; then
	[ "$drift" -eq 0 ] && echo "testu runtime files in sync" || { echo "$drift file(s) out of sync: run bin/sync-testu.sh" >&2; exit 1; }
fi
