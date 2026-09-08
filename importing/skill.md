You are an editor taking questions from a JSON document and filling out three spreadsheets. Write a Java class that will read one Input.json and output three CSV tables.

I would like you to process this Input Worksheet and insert rows into output to these sheets componentsection,componentcontent and entityquestion:
Review these tables to see some example values so you understand the mapping of data to columns.

Clear the output table of existing data before running.

Add image component types when you find a reference to an image.

The output will be in spanish

Use sequencial numbers for the ID's of each table and relationships.

Please fill in these three tables:
1. componentsection : 

Add one row for categoria found. 

2. componentcontent : Add multiple rows as needed for each componentsection with these columns:

Add one Heading componenttype for each sub-section subcategoria found. This should have  a componenttype of Heading and a contentrole of Heading. After a heading, add an "explicacion" with a type as Paragraph. Add multiple Paragraphs if needed.

content: should be the text or image reference found in the Input markdowncontent row.

componenttype: is limited to only "Asset,Heading,Paragraph,Multiple Choice Question" depending on the content found in the Input markdowncontent row. A Heading  componenttype for each sub-section such as:  1.1 Definición y características (universalidad, dignidad) After a heading put add and "explicacion" with a type as Paragraph. Add multiple Paragraphs if needed. Multiple Choice Question detailed content should be saved in entityquestion.csv table.

contentrole: Should be limited to these options: Heading,ByLine,Source,Exercise,Feature Image 
   comportamiento_observable should be set as Exercise
   "fuente": should be set as Source

ordering: is just an incremented number






