<h1>qtools</h1>

<p>qtools is a series of tools in Python3 for connecting and interacting with the Qualtrics APIs</p>

<h2>Table of contents</h2>
<ul>
    <li><a href="#requirements">Requirements</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#usage">Usage</a></li>
</ul>

<a id="requirements"><h2>Requirements</h2></a>
<p>qtools requires python 3.6 or greater and as of version 0.1.0, has no other dependencies</p>


<a id="installation"><h2>Installation</h2></a>
<p>qtools can be installed by cloning/downloading the repository and running the setup.py script with the install option</p>
<code>&lt;path_to_qtools_folder&gt;/setup.py install</code>

<p>Alternatively, you can download the latest precompiled wheel from the <b>dist</b> folder (currently version 0.1.0) and install via pip</p>
<code>python -m pip install &lt;path_to_wheel&gt;</code>

<a id="usage"><h2>Usage</h2></a>
<h3>Using the ExportClient class:</h3>
<p>The <b>ExportClient</b> class allows interaction with (as of 0.1.0) the Qualtrics List Surveys and Get Survey APIs 
to download and retrieve Survey response data. </p>
<p>To use the ExportClient class:</p>
<code>
import qtools
export_client = qtools.ExportClient(data_center, token)
</code>
<p>data_center and token are optional arguments which specify your Qualtrics data center and API token, respectively.
If omitted, ExportClient will attempt the following during initialization:</p>
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
<code>
import qtools
ec = qtools.ExportClient()
</code>

<h3>Retrieving a list of your surveys with the ExportClient class</h3>
<p>Surveys owned by a user are retrieved with the <i>get_survey_list</i> method, 
which will return a dictionary mapping survey ID to survey name</p>
<code><br>import qtools<br/>
ec = qtools.ExportClient()<br>
surveys = ec.get_survey_list()
</code>

<h3>Exporting survey response data with the ExportClient class</h3>
<p>Response data can be downloaded via the <i>export_responses</i> method:</p>
<code><br>import qtools<br/>
ec = qtools.ExportClient()<br>
surveys = ec.export_responses(out_path, survey_id, file_format, report_progress=True,
                              update_every=0.5, **kwargs)
</code>
<p><i>export_responses</i> accepts the following arguments:</p>
<ul>
    <li><i>out_path</i>: The path at which exported responses should be saved</li>
    <li><i>survey_id</i>: The qualtrics ID of the survey whose responses are to be exported</li>
    <li><i>file_format</i>: Specifies the file format to be downloaded. Accepts the following values from the <b>constants</b> module:<br>
    Format.CSV,<br>
    Format.JSON,<br>
    Format.NDJSON,<br>
    Format.SPSS,<br>
    Format.TSV,<br>
    Format.XML<br></li>
    <li><i>report_progress</i>: Specifies whether to report the progress of the export download. Default True</li>
    <li><i>update_every</i>: Specifies how often (in seconds) to check the progress of export downloads. Default 0.5</li>
</ul>

<p>export_responses also accepts a variety of keyword arguments as allowed by the Export API 
(see  the 'Body Params' section of the 
<a href="https://api.qualtrics.com/reference#create-response-export-new">Create Response Export API</a> 
for more details on these)</p>