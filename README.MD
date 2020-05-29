<h1>qtools</h1>

<p>qtools is a series of tools in Python3 for connecting and interacting with the Qualtrics APIs</p>

<h2>Table of contents</h2>
<ul>
    <li><a href="#requirements">Requirements</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#usage">Usage</a></li>
</ul>

<a id="requirements"><h2>Requirements</h2></a>
<p>qtools requires python 3.6 or greater. Currently, it has the following dependencies:</p>
<ul>
<li><a href="https://openpyxl.readthedocs.io/en/stable/">openpyxl >= 2.6.3</a></li>
</ul>


<a id="installation"><h2>Installation</h2></a>
<p>qtools can be installed by cloning/downloading the repository and running the setup.py script with the install option</p>
<code>&lt;path_to_qtools_folder&gt;/setup.py install</code>

<p>Alternatively, you can download the latest precompiled wheel from the <b>dist</b> folder (currently version 0.6.0) and install via pip</p>
<code>python -m pip install &lt;path_to_wheel&gt;</code>

<a id="usage"><h2>Usage</h2></a>
<h3>Using the ExportClient class:</h3>
<p>The <b>ExportClient</b> class allows interaction with (as of 0.6.0) the Qualtrics List Surveys and Get Survey APIs 
to download and retrieve Survey response data. </p>
<p>To use the ExportClient class:</p>

```python
import qtools
ec = qtools.ExportClient(data_center='your_data_center', token='your_api_token')
```
<p><i>data_center</i> and <i>token</i> are optional arguments which specify your Qualtrics data center and API token, respectively.</p>
<p>These variables can either specify the data center and API tokens directly, or point to OS environment variables which hold the appropriate values</p>
<p>If omitted, ExportClient will attempt the following during initialization:</p>
<ol>
    <li>Attempt to find and use the OS environment variables <i>Q_DATA_CENTER</i> and <i>Q_API_TOKEN</i> 
    for the data_center and token parameters, respectively</li>
    <li>if step 1 fails, prompt the user for these values via password prompts</li>
</ol>

<p>If either argument is specified, Export client will attempt the following during initialization:</p>
<ol>
    <li>Attempt to find an OS Environment variable by the name specifed</li>
    <li>if step 1 fails, assume the user-provided value is the data center/token</li>
</ol>
<p>The preferred usage is to create the OS environment variables <i>Q_DATA_CENTER</i> and
<i>Q_API_TOKEN</i> and populate them with your data center and API token, 
then call the parameterless constructor:</p>

```python
from qtools import *
ec = ExportClient()
```

<p>For instructions of locating your data center and API tokens, see <a href="https://api.qualtrics.com/docs/finding-qualtrics-ids">https://api.qualtrics.com/docs/finding-qualtrics-ids</a></p>
<p>for instructions regarding environmental variables, see:</p>
<ul>
    <li>windows: <a href="https://docs.oracle.com/en/database/oracle/r-enterprise/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html">Oracle.com</a></li>
    <li>linux: <a href="https://www.serverlab.ca/tutorials/linux/administration-linux/how-to-set-environment-variables-in-linux/">serverlab.ca</a></li>
    <li>mac: <a href="https://medium.com/@himanshuagarwal1395/setting-up-environment-variables-in-macos-sierra-f5978369b255">Himanshu Aggarwal's blog</a></li>
</ul>


<h3>Retrieving a list of your surveys with the ExportClient class</h3>
<p>Surveys owned by a user are retrieved with the <i>get_survey_list</i> method, 
which will return a dictionary mapping survey ID to survey name</p>

```python
import qtools
ec = qtools.ExportClient()
surveys = ec.get_survey_list()
```

<h3>Exporting survey response data with the ExportClient class</h3>
<p>Response data can be downloaded via the <i>export_responses</i> method:</p>

```python
from qtools import *
ec = ExportClient()
ec.export_responses(out_path="path_to_save", survey_id="qualtrics_id", file_format=Format.SPSS, 
                    report_progress=True, update_every=0.5, **kwargs)
```

<p><i>export_responses</i> accepts the following arguments:</p>
<ul>
    <li><i>out_path</i>: The path at which exported responses should be saved</li>
    <li><i>survey_id</i>: The qualtrics ID of the survey whose responses are to be exported.</li>
    <li><i>locator</i>: A callable which returns the ID of the survey to be exported if survey_id is not specified.
    Note that failure to specify both survey_id and locator will cause a prompt for users to input a survey ID</li>
    <li><i>file_format</i>: Specifies the file format to be downloaded. Accepts the following values from the <b>constants</b> module:<br>
    Format.CSV,<br>
    Format.JSON,<br>
    Format.NDJSON,<br>
    Format.SPSS,<br>
    Format.TSV,<br>
    Format.XML<br></li>
    <li><i>report_progress</i>: Specifies whether to report the progress of the export download. Default True</li>
    <li><i>update_every</i>: Specifies how often (in seconds) to check the progress of export downloads. Default 0.5</li>
    <li><i>survey_locator</i>: Callable which returns a survey ID if survey_id is not specified. Optional</li>
</ul>

<p>export_responses also accepts a variety of keyword arguments as allowed by the Export API 
(see  the 'Body Params' section of the 
<a href="https://api.qualtrics.com/reference#create-response-export-new">Create Response Export API</a> 
for more details on these)</p>

<h3>Exporting Survey Definitions and Data Dictionaries/Codebooks</h3>
<p>Survey definition data and codebooks can be downloaded with the  <i>export_survey_definition</i> and <i>export_codebook</i> methods, respectively:</p>

```python
from qtools import *

ec = ExportClient
survey_def = ec.export_survey_definition(survey_id='surveyID', format=Format.JSON)
```

<p>The <i>export_survey_definition</i> method accepts the following arguments:</p>
<ul>
    <li><i>survey_id</i>: The ID of the survey whose definition is to be exported</li>
    <li><i>locator</i>: A callable which returns the ID of the survey to be exported, if survey_id is not specified</li>
    <li><i>format</i>: The format of the data. Format.JSON for JSON data or format.TXT for text. Default Format.JSON</li>
</ul>
<p><i>export_survey_definition</i> returns either a JSON object or text (which can be converted to JSON), depending on the value provided to format</p>

```python
from qtools import *
ec = ExportClient()
codebook = ec.export_codebook(survey_id='surveyID')  # type: openpyxl.Workbook
codebook.save("path_to_save")
```

<p>The <i>export_codebook</i> method accepts the following arguments:</p>
<ul>
    <li><i>survey_id</i>: The ID of the survey whose definition is to be exported</li>
    <li><i>locator</i>: A callable which returns the ID of the survey to be exported, if survey_id is not specified</li>
</ul>
<p><i>export_codebook</i> returns an <a href="https://openpyxl.readthedocs.io/en/stable/api/openpyxl.workbook.workbook.html">openpyxl.Workbook</a> object.
The resulting workbook will contain one worksheet for each block of the survey. 
Each worksheet will contain descriptions of the <i>variables</i> exported into a dataset via the <a href="https://api.qualtrics.com/reference#create-response-export-new">Survey Response Exports API</a>,
 including a variable's name, label, and value labels (if any).</p>