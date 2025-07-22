"Please create a comprehensive Python project that leverages FastAPI, Generative AI (Gemini), and SQL Server to process job descriptions. The project should fulfill the following requirements step-by-step:

1. FastAPI Application Setup & File Upload:

Develop a FastAPI application.

Create an endpoint (e.g., /upload-jd) that accepts file uploads.

This endpoint should be capable of receiving job description files in both PDF (.pdf) and Microsoft Word (.docx) formats.

Implement robust error handling for unsupported file types or upload failures.

2. Job Description Text Extraction:

Within the FastAPI application, after a file is uploaded, extract the plain text content from the uploaded PDF or DOCX file.

For PDF files, use a library like pypdf (or PyPDF2).

For DOCX files, use python-docx.

Ensure the extracted text is clean and ready for AI processing.

3. Generative AI (Gemini) for Key Detail Extraction:

Integrate with the Gemini API (specifically gemini-2.0-flash) to process the extracted job description text.

Craft a prompt for the Gemini model that instructs it to identify and extract the following key details from the job description:

job_title (e.g., "Software Engineer", "Data Scientist")

company_name (e.g., "Google", "Microsoft")

location (e.g., "Bengaluru, India", "Remote", "New York, NY")

experience_required (e.g., "5+ years", "Entry-level", "Senior")

qualifications (a list of required skills, degrees, certifications)

responsibilities (a list of key duties and tasks)

employment_type (e.g., "Full-time", "Contract", "Part-time")

primary_skills (a list of core, essential skills for the role)

secondary_skills (a list of highly desirable, but not strictly mandatory skills)

tertiary_skills (a list of bonus or 'nice-to-have' skills)

The AI's response must be a JSON object with these keys, ensuring easy parsing within your FastAPI application. Define a clear JSON schema for the expected output in your prompt to the AI.

4. SQL Server Database Interaction:

Define a SQL Server table named job_descriptions with columns corresponding to the key details extracted by the AI (e.g., id (PRIMARY KEY, INT IDENTITY), job_title, company_name, location, experience_required, qualifications (TEXT/NVARCHAR(MAX)), responsibilities (TEXT/NVARCHAR(MAX)), employment_type, primary_skills (TEXT/NVARCHAR(MAX)), secondary_skills (TEXT/NVARCHAR(MAX)), tertiary_skills (TEXT/NVARCHAR(MAX)), file_path (NVARCHAR(255))).

Note: For qualifications, responsibilities, primary_skills, secondary_skills, and tertiary_skills, which are lists, you should store them as JSON strings (e.g., JSON.stringify(list)) in the SQL Server TEXT or NVARCHAR(MAX) columns and parse them back into lists when retrieving.

Use the pyodbc library to connect to your SQL Server database.

Implement a function to insert the extracted key details into the job_descriptions table.

Ensure proper error handling for database connection and insertion failures.

Important: Provide placeholder connection string details for pyodbc (e.g., DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server_name;DATABASE=your_database_name;UID=your_username;PWD=your_password).

5. File Storage with Unique Naming:

Before processing, save the original uploaded job description file to a designated local folder (e.g., jd_uploads).

Ensure each saved file has a unique name (e.g., using uuid.uuid4() combined with the original file extension) to prevent naming conflicts.

Store the unique file path in the file_path column of your SQL Server table.

Deliverables:

A complete FastAPI application (main.py or similar) with all the described functionalities.

Clear comments throughout the code explaining each section, function, and logic.

A requirements.txt file listing all necessary Python packages.

Instructions on how to run the FastAPI application and how to set up the SQL Server table (e.g., a simple SQL CREATE TABLE statement).

A brief explanation of how to configure the Gemini API key and SQL Server connection details."