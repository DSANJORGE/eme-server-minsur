import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Reads the "Input Worksheet" (Input.json - one entry per question, in Spanish) and writes three
 * output tables: componentsection.csv, componentcontent.csv and entityquestion.csv.
 *
 * Usage: java QuestionBankImporter [inputJsonPath] [outputDirectory]
 *
 * Defaults: inputJsonPath = "Input.json", outputDirectory = "."
 *
 * Mapping rules: - componentsection: one row per distinct "categoria" (in first-seen order). -
 * componentcontent, per question, in document order: Heading (componenttype=Heading,
 * contentrole=Heading) - emitted once per "subcategoria", only when it changes from the previous
 * question's subcategoria. Asset (componenttype=Asset, contentrole=Feature Image) - image reference
 * ("imagen_url"). Paragraph (componenttype=Paragraph,contentrole=ByLine) - intro caption text. MCQ
 * (componenttype=MCQ) - links to the matching entityquestion.csv row via questionid; the full
 * question content lives in entityquestion.csv, not here. Paragraph (contentrole=ByLine) -
 * "explicacion" (and, if present, a second Paragraph for "distractores" - "Add multiple Paragraphs
 * if needed"). Paragraph (contentrole=Excersise) - "comportamiento_observable". Paragraph
 * (contentrole=Source) - "fuente". - entityquestion: one row per question.
 *
 * IDs across all three tables, and the componentcontent "orderingid" column, are plain sequential
 * counters (1, 2, 3, ...).
 */
public class QuestionBankImporter
{

    private static final List<String> COMPONENTSECTION_HEADER = List.of("id", "name", "ordering", "playbackentitymoduleid", "playbackentityid", "skills");
    private static final List<String> COMPONENTCONTENT_HEADER = List.of("id", "componenttype", "contentrole", "content", "componentsectionid", "questionid", "ordering");
    private static final List<String> ENTITYQUESTION_HEADER =
        List.of("id", "question", "correctoption", "cognitivelevel", "option_a", "option_b", "option_c", "option_d", "option_e", "option_f", "rationale");
    private static final int OPTION_COLUMN_COUNT = 6;

    public static void main(String[] args) throws IOException
    {
        String inputPath = args.length > 0 ? args[0] : "Input.json";
        String outputDir = args.length > 1 ? args[1] : ".";

        String json = Files.readString(Paths.get(inputPath), StandardCharsets.UTF_8);
        @SuppressWarnings("unchecked")
        Map<String, Object> root = (Map<String, Object>) new JsonParser(json).parse();
        @SuppressWarnings("unchecked")
        List<Object> preguntas = (List<Object>) root.get("preguntas");

        // ---- componentsection: one row per distinct "categoria" ----
        Map<String, Integer> categoriaToSectionId = new LinkedHashMap<>();
        for (Object o : preguntas)
        {
            @SuppressWarnings("unchecked")
            Map<String, Object> q = (Map<String, Object>) o;
            categoriaToSectionId.computeIfAbsent(str(q.get("categoria")), k -> categoriaToSectionId.size() + 1);
        }
        List<List<String>> sectionRows = new ArrayList<>();
        for (Map.Entry<String, Integer> e : categoriaToSectionId.entrySet())
        {
            String id = String.valueOf(e.getValue());
            sectionRows.add(List.of(id, e.getKey(), id, "", "", ""));
        }

        // ---- componentcontent + entityquestion, one pass over preguntas ----
        List<List<String>> contentRows = new ArrayList<>();
        List<List<String>> questionRows = new ArrayList<>();
        int contentId = 1;
        int ordering = 1;
        int questionId = 0;
        String lastSubcategoria = null;

        for (Object o : preguntas)
        {
            @SuppressWarnings("unchecked")
            Map<String, Object> q = (Map<String, Object>) o;
            questionId++;
            String qid = String.valueOf(questionId);
            int sectionId = categoriaToSectionId.get(str(q.get("categoria")));

            String subcategoria = str(q.get("subcategoria"));
            if (!subcategoria.equals(lastSubcategoria))
            {
                contentRows.add(contentRow(contentId++, "Heading", subcategoria, "Heading", sectionId, "", ordering++));
                lastSubcategoria = subcategoria;
            }

            String imagenUrl = str(q.get("imagen_url"));
            if (!imagenUrl.isEmpty())
            {
                contentRows.add(contentRow(contentId++, "Asset", imagenUrl, "Feature Image", sectionId, qid, ordering++));
            }

            String caption = str(q.get("caption"));
            if (!caption.isEmpty())
            {
                contentRows.add(contentRow(contentId++, "Paragraph", caption, "ByLine", sectionId, qid, ordering++));
            }

            contentRows.add(contentRow(contentId++, "Multiple Choice Question", "", "", sectionId, qid, ordering++));

            String explicacion = str(q.get("explicacion"));
            if (!explicacion.isEmpty())
            {
                contentRows.add(contentRow(contentId++, "Paragraph", explicacion, "ByLine", sectionId, qid, ordering++));
            }
            String distractores = str(q.get("distractores"));
            if (!distractores.isEmpty())
            {
                contentRows.add(contentRow(contentId++, "Paragraph", distractores, "ByLine", sectionId, qid, ordering++));
            }

            String comportamiento = str(q.get("comportamiento_observable"));
            if (!comportamiento.isEmpty())
            {
                contentRows.add(contentRow(contentId++, "Paragraph", comportamiento, "Exercise", sectionId, qid, ordering++));
            }

            String fuente = str(q.get("fuente"));
            if (!fuente.isEmpty())
            {
                contentRows.add(contentRow(contentId++, "Paragraph", fuente, "Source", sectionId, qid, ordering++));
            }

            @SuppressWarnings("unchecked")
            List<Object> opciones = (List<Object>) q.get("opciones");
            List<String> row = new ArrayList<>();
            row.add(qid);
            row.add(str(q.get("enunciado")));
            row.add(str(q.get("correcta_letra")));
            row.add(str(q.get("dificultad")));
            for (int i = 0; i < OPTION_COLUMN_COUNT; i++)
            {
                row.add(i < opciones.size() ? str(opciones.get(i)) : "");
            }
            String rationale = distractores.isEmpty() ? explicacion : explicacion + " " + distractores;
            row.add(rationale);
            questionRows.add(row);
        }

        Path outDir = Paths.get(outputDir);
        Files.createDirectories(outDir);
        writeCsv(outDir.resolve("componentsection.csv"), COMPONENTSECTION_HEADER, sectionRows);
        writeCsv(outDir.resolve("componentcontent.csv"), COMPONENTCONTENT_HEADER, contentRows);
        writeCsv(outDir.resolve("entityquestion.csv"), ENTITYQUESTION_HEADER, questionRows);

        System.out.println("componentsection rows: " + sectionRows.size());
        System.out.println("componentcontent rows: " + contentRows.size());
        System.out.println("entityquestion rows:   " + questionRows.size());
    }

    private static List<String> contentRow(int id, String componentType, String content, String contentRole, int sectionId, String questionId, int ordering)
    {
        return List.of(String.valueOf(id), componentType, content, contentRole, String.valueOf(sectionId), questionId, String.valueOf(ordering));
    }

    private static String str(Object o)
    {
        return o == null ? "" : String.valueOf(o).trim();
    }

    // ==================================================================
    // Minimal CSV writer (RFC4180 quoting). Overwrites/truncates any
    // existing file, satisfying "clear the output table before running".
    // ==================================================================

    static void writeCsv(Path path, List<String> header, List<List<String>> rows) throws IOException
    {
        try (BufferedWriter w = Files.newBufferedWriter(path, StandardCharsets.UTF_8))
        {
            w.write(toCsvLine(header));
            w.write("\n");
            for (List<String> row : rows)
            {
                w.write(toCsvLine(row));
                w.write("\n");
            }
        }
    }

    static String toCsvLine(List<String> fields)
    {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < fields.size(); i++)
        {
            if (i > 0)
            {
                sb.append(',');
            }
            sb.append(csvEscape(fields.get(i)));
        }
        return sb.toString();
    }

    static String csvEscape(String value)
    {
        if (value == null)
        {
            return "";
        }
        if (value.indexOf(',') < 0 && value.indexOf('"') < 0 && value.indexOf('\n') < 0 && value.indexOf('\r') < 0)
        {
            return value;
        }
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }

    // ==================================================================
    // Minimal recursive-descent JSON parser (objects, arrays, strings with
    // escapes, numbers, booleans, null). No external dependencies.
    // ==================================================================

    static class JsonParser
    {
        private final String s;
        private int i;

        JsonParser(String s) {
            this.s = s;
        }

        Object parse()
        {
            skipWs();
            Object v = parseValue();
            skipWs();
            return v;
        }

        private void skipWs()
        {
            while (i < s.length() && Character.isWhitespace(s.charAt(i)))
            {
                i++;
            }
        }

        private Object parseValue()
        {
            skipWs();
            char c = s.charAt(i);
            switch (c)
            {
                case '{':
                    return parseObject();
                case '[':
                    return parseArray();
                case '"':
                    return parseString();
                case 't':
                    i += 4;
                    return Boolean.TRUE;
                case 'f':
                    i += 5;
                    return Boolean.FALSE;
                case 'n':
                    i += 4;
                    return null;
                default:
                    return parseNumber();
            }
        }

        private Map<String, Object> parseObject()
        {
            Map<String, Object> map = new LinkedHashMap<>();
            i++; // consume '{'
            skipWs();
            if (s.charAt(i) == '}')
            {
                i++;
                return map;
            }
            while (true)
            {
                skipWs();
                String key = parseString();
                skipWs();
                i++; // consume ':'
                Object value = parseValue();
                map.put(key, value);
                skipWs();
                char c = s.charAt(i++);
                if (c == '}')
                {
                    break;
                }
                // otherwise c == ',', continue to next key/value pair
            }
            return map;
        }

        private List<Object> parseArray()
        {
            List<Object> list = new ArrayList<>();
            i++; // consume '['
            skipWs();
            if (s.charAt(i) == ']')
            {
                i++;
                return list;
            }
            while (true)
            {
                list.add(parseValue());
                skipWs();
                char c = s.charAt(i++);
                if (c == ']')
                {
                    break;
                }
                // otherwise c == ',', continue to next element
            }
            return list;
        }

        private String parseString()
        {
            StringBuilder sb = new StringBuilder();
            i++; // consume opening quote
            while (true)
            {
                char c = s.charAt(i++);
                if (c == '"')
                {
                    break;
                }
                if (c == '\\')
                {
                    char e = s.charAt(i++);
                    switch (e)
                    {
                        case '"':
                            sb.append('"');
                            break;
                        case '\\':
                            sb.append('\\');
                            break;
                        case '/':
                            sb.append('/');
                            break;
                        case 'b':
                            sb.append('\b');
                            break;
                        case 'f':
                            sb.append('\f');
                            break;
                        case 'n':
                            sb.append('\n');
                            break;
                        case 'r':
                            sb.append('\r');
                            break;
                        case 't':
                            sb.append('\t');
                            break;
                        case 'u':
                            sb.append((char) Integer.parseInt(s.substring(i, i + 4), 16));
                            i += 4;
                            break;
                        default:
                            sb.append(e);
                    }
                }
                else
                {
                    sb.append(c);
                }
            }
            return sb.toString();
        }

        private Double parseNumber()
        {
            int start = i;
            while (i < s.length() && "-+.eE0123456789".indexOf(s.charAt(i)) >= 0)
            {
                i++;
            }
            return Double.parseDouble(s.substring(start, i));
        }
    }
}
