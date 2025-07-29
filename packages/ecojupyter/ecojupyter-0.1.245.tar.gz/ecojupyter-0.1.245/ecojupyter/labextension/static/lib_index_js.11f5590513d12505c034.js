"use strict";
(self["webpackChunkecojupyter"] = self["webpackChunkecojupyter"] || []).push([["lib_index_js"],{

/***/ "./lib/api/apiScripts.js":
/*!*******************************!*\
  !*** ./lib/api/apiScripts.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   cleanExperimentMetadata: () => (/* binding */ cleanExperimentMetadata),
/* harmony export */   createExperimentIdFolderSh: () => (/* binding */ createExperimentIdFolderSh),
/* harmony export */   exportSendJson: () => (/* binding */ exportSendJson),
/* harmony export */   generateExperimentIdAndStartTime: () => (/* binding */ generateExperimentIdAndStartTime),
/* harmony export */   getAndSetWorkflowId: () => (/* binding */ getAndSetWorkflowId),
/* harmony export */   getEndTime: () => (/* binding */ getEndTime),
/* harmony export */   getExperimentId: () => (/* binding */ getExperimentId),
/* harmony export */   getExperimentList: () => (/* binding */ getExperimentList),
/* harmony export */   getOS: () => (/* binding */ getOS),
/* harmony export */   getSessionMetrics: () => (/* binding */ getSessionMetrics),
/* harmony export */   getTime: () => (/* binding */ getTime),
/* harmony export */   getUsernameSh: () => (/* binding */ getUsernameSh),
/* harmony export */   getWorkflowList: () => (/* binding */ getWorkflowList),
/* harmony export */   installPrometheusScaphandre: () => (/* binding */ installPrometheusScaphandre),
/* harmony export */   moveExperimentFolder: () => (/* binding */ moveExperimentFolder),
/* harmony export */   saveRoCrateMetadata: () => (/* binding */ saveRoCrateMetadata),
/* harmony export */   saveSessionMetrics: () => (/* binding */ saveSessionMetrics),
/* harmony export */   saveStartEndTime: () => (/* binding */ saveStartEndTime),
/* harmony export */   saveUsernameSh: () => (/* binding */ saveUsernameSh)
/* harmony export */ });
/* harmony import */ var _helpers_utils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../helpers/utils */ "./lib/helpers/utils.js");

const getOS = `
uname_str="$(uname -s)"
os_info=""

case "\${uname_str}" in
    Linux*)
        if [ -f /etc/os-release ]; then
            # Parse common distro info
            . /etc/os-release
            os_info="Linux ($NAME $VERSION)"
        else
            os_info="Linux (Unknown distro)"
        fi
        ;;
    Darwin*)
        # Use sw_vers for macOS version info
        if command -v sw_vers &>/dev/null; then
            product_name=$(sw_vers -productName)
            product_version=$(sw_vers -productVersion)
            os_info="Mac ($product_name $product_version)"
        else
            os_info="Mac (Unknown version)"
        fi
        ;;
    CYGWIN*|MINGW*|MSYS*)
        # Try to get Windows version info
        if command -v cmd.exe &>/dev/null; then
            win_ver=$(cmd.exe /c ver | tr -d '\r')
            os_info="Windows ($win_ver)"
        else
            os_info="Windows (Unknown version)"
        fi
        ;;
    *)
        os="UNKNOWN:\${uname_str}"
        os_info="Unknown OS"
        ;;
esac
export OS_INFO="$os_info"
`;
const exportSendJson = (props) => `
%%bash

${getOS}

export EXPORT_JSON_PATH=".lib/export_metadata.json"

name=${(0,_helpers_utils__WEBPACK_IMPORTED_MODULE_0__.toLowerCaseWithUnderscores)(props.title)}
title="${props.title}"
creator="${props.creator}"
workflow_id="${props.workflow_id}"
experiment_id="${props.experiment_id}"
os="$OS_INFO"
email="${props.email}"
pi="${props.orcid}"
metrics="${props.session_metrics}"
platform="GreenDIGIT"
node="node_01"
lang="python"
creation_date="${props.creation_date}"
project_id="greendigit_development"

json_payload=$(jq -n \
  --arg name $name \
  --arg title "$title" \
  --arg creator "$creator" \
  --arg workflow_id "$workflow_id" \
  --arg experiment_id "$experiment_id" \
  --arg os "$os" \
  --arg email "$email" \
  --arg pi "$pi" \
  --arg metrics "$metrics" \
  --arg platform "$platform" \
  --arg node "$node" \
  --arg lang "$lang" \
  --arg creation_date "$creation_date" \
  --arg project_id "$project_id" \
  '{
    name: $name,
    title: $title,
    license_id: "AFL-3.0",
    private: "False",
    notes: "GD call test environmnet.",
    url: "null",
    tags: [{ name: "Test" }],
    resources: [{
      name: "RO-Crate metadata",
      url: "https://data.d4science.net/5Apv",
      format: "zip"
    }],
    extras: [
      { key: "Creation Date", value: $creation_date },
      { key: "Creator", value: $creator },
      { key: "Creator Email", value: $email },
      { key: "Creator Name PI (Principal Investigator)", value: $pi },
      { key: "Environment OS", value: $os },
      { key: "Environment Platform", value: $platform },
      { key: "Experiment Dependencies", value: "null" },
      { key: "Experiment ID", value: $experiment_id },
      { key: "GreenDIGIT Node", value: $node },
      { key: "Programming Language", value: $lang },
      { key: "Project ID", value: $project_id },
      { key: "Session reading metrics", value: $metrics },
      { key: "system:type", value: "Experiment" }
    ]
  }')

echo $json_payload > $EXPORT_JSON_PATH

AUTH_TOKEN="${props.token}"

json_obj=$(jq . ".lib/export_metadata.json")
echo $json_obj
curl --header "Content-Type: application/json" \
    --header "Authorization: Bearer $AUTH_TOKEN" \
    --location "https://api.d4science.org/gcat/items" \
    --data-raw "$json_obj"
`;
const saveUsernameSh = `
%%bash
mkdir -p .lib
echo \${HOSTNAME#jupyter-} > .lib/hostname
echo "Username saved to .lib/hostname"
`;
const generateExperimentIdAndStartTime = `
import os
from datetime import UTC, datetime, timezone
import hashlib

ts = datetime.now(UTC).strftime("%Y-%m-%d %H:%M")
os.environ["START_TIME"] = ts
experiment_id = f"experiment-{hashlib.sha256(ts.encode()).hexdigest()[:8]}-{ts}"
os.environ["EXPERIMENT_ID"] = experiment_id
print("Created experiment ID environment var $EXPERIMENT_ID")
`;
const createExperimentIdFolderSh = `
%%bash
mkdir -p ".lib/experiments/$WORKFLOW_ID/$EXPERIMENT_ID"
echo "Created Experiment ID folder $EXPERIMENT_ID in workflow $WORKFLOW_ID"
`;
const getExperimentId = `
import os
print("Getting experiment ID: " + os.environ["EXPERIMENT_ID"])
`;
const getUsernameSh = `
%%bash
echo "$(cat .lib/hostname)"
`;
const installPrometheusScaphandre = `
%%bash
curl -O https://raw.githubusercontent.com/g-uva/JupyterK8sMonitor/refs/heads/master/scaphandre-prometheus-ownpod/install-scaphandre-prometheus.sh
sudo chmod +x install-scaphandre-prometheus.sh
./install-scaphandre-prometheus.sh
sudo rm -rf ./install-scaphandre-prometheus.sh
`;
const cleanExperimentMetadata = `
%%bash
experiment_temp = $EXPERIMENT_ID
unset EXPERIMENT_ID
unset WORKFLOW_ID
unset START_TIME
unset END_TIME
echo "Cleared Experiment $experiment_temp metadata."
`;
const getWorkflowList = `
%%bash
BASE_PATH=".lib/experiments/"
FOLDER_NAMES=()

for dir in "$BASE_PATH"/*/; do
  [ -d "$dir" ] && FOLDER_NAMES+=("$(basename "$dir")")
done

echo "\${FOLDER_NAMES[@]}"
`;
const getExperimentList = (workflowId) => `
%%bash
BASE_PATH=".lib/experiments/${workflowId}"
FOLDER_NAMES=()

for dir in "$BASE_PATH"/*/; do
  [ -d "$dir" ] && FOLDER_NAMES+=("$(basename "$dir")")
done

echo "\${FOLDER_NAMES[@]}"
`;
const moveExperimentFolder = `
%%bash
# HOME="/home/jovyan"
HOME="."
if [ -n os.environ["$WOFKLOW_ID"] ]; then
  if [ -n os.environ["$EXPERIMENT_ID"] ]; then
    mkdir -p $HOME/experiments
    mv $HOME/.lib/experiments/$EXPERIMENT_ID $HOME/experiments/$WORKFLOW_ID/$EXPERIMENT_ID
    echo "Moved experiment: $EXPERIMENT_ID"
  else
    echo "No EXPERIMENT_ID set, skipping move."
  fi
else
  echo "No WORKFLOW_ID set, skipping move."
fi
`;
const getEndTime = `
import os
et = datetime.now(UTC).strftime("%Y-%m-%d %H:%M")
os.environ["END_TIME"] = et
`;
const saveStartEndTime = `
%%bash
start_time=$START_TIME
end_time=$END_TIME
jq -n \
    --arg start_time "$start_time" \
    --arg end_time "$end_time" \
    '{
      "start_time": $start_time,
      "end_time": $end_time
    }' > .lib/experiments/"$WORKFLOW_ID"/"$EXPERIMENT_ID"/timestamps.json
`;
const getTime = (workflow, experiment) => `
%%bash
TIMESTAMP_FILE=".lib/experiments/${workflow}/${experiment}/timestamps.json"

if [ -f "$TIMESTAMP_FILE" ]; then
  cat "$TIMESTAMP_FILE"
else
  echo -n "{ \\"start_time\\": \\"$START_TIME\\", \\"end_time\\": "
    if [ -z "$END_TIME" ]; then
      echo "null }"
    else
      echo "\\"$END_TIME\\" }"
    fi
fi
`;
const getAndSetWorkflowId = `
import os
import json
import ipykernel
import urllib.request
from jupyter_server import serverapp

def get_notebook_name():
    connection_file = os.path.basename(ipykernel.get_connection_file())
    kernel_id = connection_file.split('-', 1)[1].split('.')[0]

    for srv in serverapp.list_running_servers():
        try:
            url = srv['url']
            token = srv.get('token', '')
            if token:
                url += f'tree?token={token}'
            sessions_url = srv['url'] + 'api/sessions'
            if token:
                sessions_url += f'?token={token}'

            with urllib.request.urlopen(sessions_url) as response:
                sessions = json.load(response)
                for sess in sessions:
                    if sess['kernel']['id'] == kernel_id:
                        return os.path.basename(sess['notebook']['path']).split('.')[0]
        except Exception as e:
            pass

    return None

print(get_notebook_name())
os.environ["WORKFLOW_ID"] = get_notebook_name()
`;
const saveRoCrateMetadata = `


`;
const saveSessionMetrics = `
%%bash
username=$(cat .lib/hostname)
output_file=".lib/experiments/$WORKFLOW_ID/$EXPERIMENT_ID/metrics.csv"
sudo rm -rf $output_file
prom_url="https://mc-a4.lab.uvalight.net/prometheus-$username"
st=$(date -u -d "$START_TIME" +"%Y-%m-%dT%H:%M:%SZ")
et=$(date -u -d "$END_TIME" +"%Y-%m-%dT%H:%M:%SZ")

metric_names=$(curl -s "$prom_url/api/v1/label/__name__/values" | jq -r '.data[] | select(startswith("scaph_"))')

echo $metric_names
echo $st
echo $et

tmp_dir=".lib/tmp_metrics"
rm -rf "$tmp_dir"
mkdir -p "$tmp_dir"

for metric in $metric_names; do
  curl -s -G "$prom_url/api/v1/query_range" \\
    --data-urlencode "query=$metric" \\
    --data-urlencode "start=$st" \\
    --data-urlencode "end=$et" \\
    --data-urlencode "step=15s" | \\
    jq -r '.data.result[]?.values[] | @csv' > "$tmp_dir/$metric.csv"
done

ls -la ".lib/tmp_metrics"

first=1
for file in "$tmp_dir"/*.csv; do
  if [ $first -eq 1 ]; then
    cut -d',' -f1 "$file" > "$output_file"
    first=0
  fi
done

for file in "$tmp_dir"/*.csv; do
  cut -d',' -f2 "$file" > "$file.val"
  paste -d',' "$output_file" "$file.val" > "$output_file.tmp"
  mv "$output_file.tmp" "$output_file"
done

# Add header (except for first timestamp column which has no header)
echo -n "" > "$output_file.header"
for file in "$tmp_dir"/*.csv; do
  metric=$(basename "$file" .csv)
  echo -n ",$metric" >> "$output_file.header"
done
cat "$output_file.header" "$output_file" > "$output_file.final"
mv "$output_file.final" "$output_file"

rm -rf "$tmp_dir"

echo "CSV file generated at: $output_file" 
head -n 100 "$output_file"
`;
const getSessionMetrics = (workflowId, experimentId) => `
%%bash
echo $(cat ".lib/experiments/${workflowId}/${experimentId}/metrics.csv")
`;


/***/ }),

/***/ "./lib/api/getScaphData.js":
/*!*********************************!*\
  !*** ./lib/api/getScaphData.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ getScaphData)
/* harmony export */ });
async function getMetricData(prometheusUrl, metricName, start, end, step) {
    const url = new URL(`${prometheusUrl}/api/v1/query_range`);
    url.searchParams.set('query', metricName);
    url.searchParams.set('start', start.toString());
    url.searchParams.set('end', end.toString());
    url.searchParams.set('step', step.toString());
    const resp = await fetch(url.toString());
    return await resp.json();
}
async function getScaphMetrics(prometheusUrl) {
    const resp = await fetch(`${prometheusUrl}/api/v1/label/__name__/values`);
    const data = await resp.json();
    return data.data.filter((name) => name.startsWith('scaph_'));
}
async function getScaphData({ url, startTime, endTime }) {
    try {
        const metricNames = [];
        await getScaphMetrics(url).then(response => metricNames.push(...response));
        const step = 15;
        const results = new Map();
        for (const metricName of metricNames) {
            const metricData = await getMetricData(url, metricName, startTime, endTime, step);
            const data = metricData.data.result[0].values; // For some reason the response is within a [].
            results.set(metricName, data);
        }
        return results;
    }
    catch (error) {
        console.error('Error fetching Scaph metrics:', error);
        return new Map();
    }
}


/***/ }),

/***/ "./lib/api/handleNotebookContents.js":
/*!*******************************************!*\
  !*** ./lib/api/handleNotebookContents.js ***!
  \*******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   captureKernelOutput: () => (/* binding */ captureKernelOutput),
/* harmony export */   getHandleSessionMetrics: () => (/* binding */ getHandleSessionMetrics),
/* harmony export */   handleFirstCellExecution: () => (/* binding */ handleFirstCellExecution),
/* harmony export */   handleGetTime: () => (/* binding */ handleGetTime),
/* harmony export */   handleLastCellExecution: () => (/* binding */ handleLastCellExecution),
/* harmony export */   handleLoadExperimentList: () => (/* binding */ handleLoadExperimentList),
/* harmony export */   handleLoadWorkflowList: () => (/* binding */ handleLoadWorkflowList),
/* harmony export */   handleNotebookSessionContents: () => (/* binding */ handleNotebookSessionContents)
/* harmony export */ });
/* harmony import */ var _apiScripts__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./apiScripts */ "./lib/api/apiScripts.js");
/* harmony import */ var dayjs__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! dayjs */ "webpack/sharing/consume/default/dayjs/dayjs");
/* harmony import */ var dayjs__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(dayjs__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _helpers_utils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../helpers/utils */ "./lib/helpers/utils.js");



async function handleFirstCellExecution(panel) {
    await handleNotebookSessionContents(panel, _apiScripts__WEBPACK_IMPORTED_MODULE_1__.generateExperimentIdAndStartTime);
    await handleNotebookSessionContents(panel, _apiScripts__WEBPACK_IMPORTED_MODULE_1__.getAndSetWorkflowId);
    await handleNotebookSessionContents(panel, _apiScripts__WEBPACK_IMPORTED_MODULE_1__.createExperimentIdFolderSh);
    // await handleNotebookSessionContents(panel, installJqPackage);
}
async function handleLastCellExecution(panel) {
    try {
        await handleNotebookSessionContents(panel, _apiScripts__WEBPACK_IMPORTED_MODULE_1__.getEndTime);
        await handleNotebookSessionContents(panel, _apiScripts__WEBPACK_IMPORTED_MODULE_1__.saveSessionMetrics);
        await handleNotebookSessionContents(panel, _apiScripts__WEBPACK_IMPORTED_MODULE_1__.saveStartEndTime);
        await handleNotebookSessionContents(panel, _apiScripts__WEBPACK_IMPORTED_MODULE_1__.cleanExperimentMetadata);
    }
    catch (err) {
        console.error(err, 'Error detected');
    }
}
/**
 * @param panel NotebookPanel to handle
 * This function handles the contents of a NotebookPanel, specifically saving the username to a file.
 * It waits for the session context to be ready, then checks if a kernel is available.
 * If a kernel is found, it executes a code snippet to save the username to a file named `.lib/hostname`.
 * If the execution is successful, it logs a success message.
 * This executes each time that a Notebook is opened or refreshed.
 */
async function handleNotebookSessionContents(panel, code) {
    var _a;
    await panel.sessionContext.ready;
    const kernel = (_a = panel.sessionContext.session) === null || _a === void 0 ? void 0 : _a.kernel;
    if (kernel) {
        const future = kernel.requestExecute({ code });
        return await captureKernelOutput(future).then(output => {
            return output;
        });
    }
    else {
        console.warn('No active kernel found.');
    }
}
function captureKernelOutput(future) {
    return new Promise(resolve => {
        let result = '';
        future.onIOPub = (msg) => {
            const msgType = msg.header.msg_type;
            if (msgType === 'stream') {
                const content = msg.content;
                result += content.text;
            }
            else if (msgType === 'execute_result') {
                const content = msg.content;
                const data = content.data['text/plain'];
                result += data;
            }
            else if (msgType === 'error') {
                const content = msg.content;
                result += content.ename + ': ' + content.evalue;
            }
        };
        future.done.then(() => resolve(result.trim()));
    });
}
async function handleLoadWorkflowList(panel) {
    const experimentList = await handleNotebookSessionContents(panel, _apiScripts__WEBPACK_IMPORTED_MODULE_1__.getWorkflowList);
    return experimentList ? experimentList.split(' ') : [''];
}
async function handleLoadExperimentList(worfklowId, panel) {
    const experimentList = await handleNotebookSessionContents(panel, (0,_apiScripts__WEBPACK_IMPORTED_MODULE_1__.getExperimentList)(worfklowId));
    const entries = experimentList === null || experimentList === void 0 ? void 0 : experimentList.match(/experiment-[^\s]+ \d{2}:\d{2}/g);
    return entries !== null && entries !== void 0 ? entries : [''];
}
async function getHandleSessionMetrics(workflowId, experimentId, panel) {
    return await handleNotebookSessionContents(panel, (0,_apiScripts__WEBPACK_IMPORTED_MODULE_1__.getSessionMetrics)(workflowId, experimentId));
}
async function handleGetTime(workflowId, experimentId, panel) {
    const jsonStringTime = await handleNotebookSessionContents(panel, (0,_apiScripts__WEBPACK_IMPORTED_MODULE_1__.getTime)(workflowId, experimentId));
    if (typeof jsonStringTime === 'string') {
        const jsonTime = JSON.parse(jsonStringTime);
        const { start_time, end_time } = jsonTime;
        const differenceUnix = 60 * 60 * (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_2__.getOffsetHours)();
        const startTimeUnix = dayjs__WEBPACK_IMPORTED_MODULE_0___default()(start_time).unix() + differenceUnix;
        const endTimeUnix = end_time !== null
            ? dayjs__WEBPACK_IMPORTED_MODULE_0___default()(end_time).unix() + differenceUnix
            : dayjs__WEBPACK_IMPORTED_MODULE_0___default()().unix() + differenceUnix;
        return { startTimeUnix, endTimeUnix, start_time };
    }
    return null;
}


/***/ }),

/***/ "./lib/components/AddButton.js":
/*!*************************************!*\
  !*** ./lib/components/AddButton.js ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ AddButton)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_icons_material_AddCircleOutlineRounded__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/icons-material/AddCircleOutlineRounded */ "./node_modules/@mui/icons-material/esm/AddCircleOutlineRounded.js");



function AddButton({ handleClickButton }) {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Button, { onClick: handleClickButton, size: "small", startIcon: react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_AddCircleOutlineRounded__WEBPACK_IMPORTED_MODULE_2__["default"], null), sx: { textTransform: 'none' } }, "Add chart"));
}


/***/ }),

/***/ "./lib/components/ApiSubmitForm.js":
/*!*****************************************!*\
  !*** ./lib/components/ApiSubmitForm.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ ApiSubmitForm)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_Button__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @mui/material/Button */ "./node_modules/@mui/material/Button/Button.js");
/* harmony import */ var _mui_material_TextField__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @mui/material/TextField */ "./node_modules/@mui/material/TextField/TextField.js");
/* harmony import */ var _mui_material_Dialog__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material/Dialog */ "./node_modules/@mui/material/Dialog/Dialog.js");
/* harmony import */ var _mui_material_DialogActions__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @mui/material/DialogActions */ "./node_modules/@mui/material/DialogActions/DialogActions.js");
/* harmony import */ var _mui_material_DialogContent__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/material/DialogContent */ "./node_modules/@mui/material/DialogContent/DialogContent.js");
/* harmony import */ var _mui_material_DialogContentText__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/material/DialogContentText */ "./node_modules/@mui/material/DialogContentText/DialogContentText.js");
/* harmony import */ var _mui_material_DialogTitle__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/material/DialogTitle */ "./node_modules/@mui/material/DialogTitle/DialogTitle.js");








function ApiSubmitForm({ open, setOpen, submitValues }) {
    const handleClose = () => {
        setOpen(false);
    };
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(react__WEBPACK_IMPORTED_MODULE_0__.Fragment, null,
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Dialog__WEBPACK_IMPORTED_MODULE_1__["default"], { open: open, onClose: handleClose, slotProps: {
                paper: {
                    component: 'form',
                    onSubmit: (event) => {
                        event.preventDefault();
                        const formData = new FormData(event.currentTarget);
                        const formJson = Object.fromEntries(formData.entries());
                        const title = formJson.title;
                        const creator = formJson.creator;
                        const email = formJson.email;
                        const orcid = formJson.orcid;
                        const token = formJson.token;
                        if (typeof title === 'string' &&
                            typeof creator === 'string' &&
                            typeof email === 'string' &&
                            typeof orcid === 'string' &&
                            typeof token === 'string') {
                            submitValues({ title, creator, email, orcid, token });
                            handleClose();
                        }
                    }
                }
            } },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_DialogTitle__WEBPACK_IMPORTED_MODULE_2__["default"], null, "Submit Experiment ID to database"),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_DialogContent__WEBPACK_IMPORTED_MODULE_3__["default"], null,
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_DialogContentText__WEBPACK_IMPORTED_MODULE_4__["default"], null, "This will publish your Experiment ID in the database."),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_TextField__WEBPACK_IMPORTED_MODULE_5__["default"], { autoFocus: true, required: true, margin: "dense", id: "name", name: "email", label: "Email Address", type: "email", fullWidth: true, variant: "outlined" }),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_TextField__WEBPACK_IMPORTED_MODULE_5__["default"], { autoFocus: true, required: true, margin: "dense", id: "creator", name: "creator", label: "Creator's name", type: "text", fullWidth: true, variant: "outlined" }),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_TextField__WEBPACK_IMPORTED_MODULE_5__["default"], { autoFocus: true, required: true, margin: "dense", id: "orcid", name: "orcid", label: "ORCID", type: "text", fullWidth: true, variant: "outlined" }),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_TextField__WEBPACK_IMPORTED_MODULE_5__["default"], { autoFocus: true, required: true, margin: "dense", id: "title", name: "title", label: "Title", type: "text", fullWidth: true, variant: "outlined" }),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_TextField__WEBPACK_IMPORTED_MODULE_5__["default"], { autoFocus: true, required: true, margin: "dense", id: "token", name: "token", label: "FDMI Token", type: "text", fullWidth: true, variant: "outlined" })),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_DialogActions__WEBPACK_IMPORTED_MODULE_6__["default"], null,
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Button__WEBPACK_IMPORTED_MODULE_7__["default"], { onClick: handleClose }, "Cancel"),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Button__WEBPACK_IMPORTED_MODULE_7__["default"], { type: "submit" }, "Submit")))));
}


/***/ }),

/***/ "./lib/components/ChartWrapper.js":
/*!****************************************!*\
  !*** ./lib/components/ChartWrapper.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ ChartWrapper)
/* harmony export */ });
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _NumberInput__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./NumberInput */ "./lib/components/NumberInput.js");
/* harmony import */ var _RefreshButton__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./RefreshButton */ "./lib/components/RefreshButton.js");
/* harmony import */ var _DeleteIconButton__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./DeleteIconButton */ "./lib/components/DeleteIconButton.js");
/* harmony import */ var _helpers_constants__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../helpers/constants */ "./lib/helpers/constants.js");






function debounce(func, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => func(...args), delay);
    };
}
function ChartWrapper({ keyId, src, width, height, onDelete }) {
    const iframeRef = react__WEBPACK_IMPORTED_MODULE_1___default().useRef(null);
    const [refreshRateS, setRefreshRateS] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(_helpers_constants__WEBPACK_IMPORTED_MODULE_2__.DEFAULT_REFRESH_RATE);
    const initialSrcWithRefresh = `${src}&refresh=${refreshRateS}s`;
    const [iframeSrc, setIframeSrc] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(initialSrcWithRefresh);
    function refreshUrl() {
        setIframeSrc(prevState => {
            const base = prevState.split('&refresh=')[0];
            return `${base}&refresh=${refreshRateS}s`;
        });
    }
    react__WEBPACK_IMPORTED_MODULE_1___default().useEffect(() => {
        refreshUrl();
        const intervalId = setInterval(() => {
            refreshUrl();
        }, refreshRateS * 1000);
        // Whenever the refresh interval is cleared.
        return () => clearInterval(intervalId);
    }, [refreshRateS]);
    function handleRefreshClick() {
        if (iframeRef.current) {
            const copy_src = structuredClone(iframeRef.current.src);
            iframeRef.current.src = copy_src;
        }
    }
    // Call the debounced function on number change
    function handleNumberChange(value) {
        const parsedValue = Number(value);
        if (!isNaN(parsedValue)) {
            debouncedSetRefreshRateS(parsedValue);
        }
    }
    // Create a debounced version of setRefreshRateS
    // Using 200ms delay instead of 2ms for a noticeable debounce effect.
    const debouncedSetRefreshRateS = react__WEBPACK_IMPORTED_MODULE_1___default().useMemo(() => debounce((value) => setRefreshRateS(value), 1000), []);
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("iframe", { src: iframeSrc, width: width, height: height, sandbox: "allow-scripts allow-same-origin", ref: iframeRef, id: `iframe-item-${keyId}` }),
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid2, null,
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_RefreshButton__WEBPACK_IMPORTED_MODULE_3__["default"], { handleRefreshClick: handleRefreshClick }),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_NumberInput__WEBPACK_IMPORTED_MODULE_4__["default"]
            // currentRefreshValue={refreshRateS}
            , { 
                // currentRefreshValue={refreshRateS}
                handleRefreshNumberChange: newValue => handleNumberChange(newValue) }),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_DeleteIconButton__WEBPACK_IMPORTED_MODULE_5__["default"], { handleClickButton: () => onDelete(keyId) }))));
}


/***/ }),

/***/ "./lib/components/DeleteIconButton.js":
/*!********************************************!*\
  !*** ./lib/components/DeleteIconButton.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ DeleteIconButton)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_icons_material_DeleteOutlineRounded__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/icons-material/DeleteOutlineRounded */ "./node_modules/@mui/icons-material/esm/DeleteOutlineRounded.js");



function DeleteIconButton({ handleClickButton }) {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton, { onClick: handleClickButton, size: "small" },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_DeleteOutlineRounded__WEBPACK_IMPORTED_MODULE_2__["default"], null)));
}


/***/ }),

/***/ "./lib/components/FetchMetricsComponents.js":
/*!**************************************************!*\
  !*** ./lib/components/FetchMetricsComponents.js ***!
  \**************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ FetchMetricsComponent)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _pages_WelcomePage__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../pages/WelcomePage */ "./lib/pages/WelcomePage.js");
/* harmony import */ var _mui_icons_material_RefreshRounded__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/icons-material/RefreshRounded */ "./node_modules/@mui/icons-material/esm/RefreshRounded.js");



// import FetchAutomatic from './FetchAutomatic';

function FetchMetricsComponent({ fetchMetrics, 
// fetchInterval,
// setFetchInterval,
// setIsFetchMetrics,
handleInstallMetrics }) {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { ..._pages_WelcomePage__WEBPACK_IMPORTED_MODULE_2__.styles.buttonGrid, mb: 0 } },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Button, { variant: "outlined", onClick: handleInstallMetrics, sx: { maxHeight: '40px' }, startIcon: react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_RefreshRounded__WEBPACK_IMPORTED_MODULE_3__["default"], null) }, "Install metrics' agent"),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Button
        // disabled={username.length === 0}
        , { 
            // disabled={username.length === 0}
            variant: "outlined", onClick: fetchMetrics, sx: { maxHeight: '40px' }, startIcon: react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_RefreshRounded__WEBPACK_IMPORTED_MODULE_3__["default"], null) }, "Refresh Metrics")));
}


/***/ }),

/***/ "./lib/components/GoBackButton.js":
/*!****************************************!*\
  !*** ./lib/components/GoBackButton.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ GoBackButton)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_icons_material_ArrowBackRounded__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/icons-material/ArrowBackRounded */ "./node_modules/@mui/icons-material/esm/ArrowBackRounded.js");



function GoBackButton({ handleClick }) {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton, { onClick: handleClick, size: "small" },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_ArrowBackRounded__WEBPACK_IMPORTED_MODULE_2__["default"], null)));
}


/***/ }),

/***/ "./lib/components/JupyterDialogWarning.js":
/*!************************************************!*\
  !*** ./lib/components/JupyterDialogWarning.js ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ JupyterDialogWarning)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);

function JupyterDialogWarning({ message, buttonLabel, action }) {
    (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
        title: 'Warning ⚠️',
        body: message !== null && message !== void 0 ? message : 'There was some error, please contact the admin.',
        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton({ label: buttonLabel !== null && buttonLabel !== void 0 ? buttonLabel : 'Continue' })]
    }).then(result => {
        // The dialog closes automatically, no need to manually trigger it.
        if (result.button.accept) {
            action === null || action === void 0 ? void 0 : action();
        }
    });
}


/***/ }),

/***/ "./lib/components/KPIComponent.js":
/*!****************************************!*\
  !*** ./lib/components/KPIComponent.js ***!
  \****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   KPIComponent: () => (/* binding */ KPIComponent),
/* harmony export */   calculateKPIs: () => (/* binding */ calculateKPIs)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _helpers_types__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../helpers/types */ "./lib/helpers/types.js");
/* harmony import */ var _helpers_utils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../helpers/utils */ "./lib/helpers/utils.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_icons_material_SolarPowerOutlined__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @mui/icons-material/SolarPowerOutlined */ "./node_modules/@mui/icons-material/esm/SolarPowerOutlined.js");
/* harmony import */ var _mui_icons_material_BoltOutlined__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @mui/icons-material/BoltOutlined */ "./node_modules/@mui/icons-material/esm/BoltOutlined.js");
/* harmony import */ var _mui_icons_material_EnergySavingsLeafOutlined__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @mui/icons-material/EnergySavingsLeafOutlined */ "./node_modules/@mui/icons-material/esm/EnergySavingsLeafOutlined.js");
/* harmony import */ var _mui_icons_material_RefreshRounded__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @mui/icons-material/RefreshRounded */ "./node_modules/@mui/icons-material/esm/RefreshRounded.js");
/* harmony import */ var _KpiValue__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./KpiValue */ "./lib/components/KpiValue.js");
/* harmony import */ var _helpers_constants__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../helpers/constants */ "./lib/helpers/constants.js");
/* harmony import */ var _pages_WelcomePage__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../pages/WelcomePage */ "./lib/pages/WelcomePage.js");

// import dayjs from 'dayjs';








// import getDynamicCarbonIntensity from '../api/getCarbonIntensityData';


// Default static values
const defaultCarbonIntensity = 400;
const embodiedEmissions = 50000;
// const hepScore23 = 42.3;
async function prometheusMetricsProxy(type, raw) {
    var _a, _b;
    // const carbonIntensity =
    //   (await getDynamicCarbonIntensity()) ?? defaultCarbonIntensity;
    const carbonIntensity = defaultCarbonIntensity;
    const rawEnergyConsumed = raw.get(_helpers_types__WEBPACK_IMPORTED_MODULE_2__.METRIC_KEY_MAP.energyConsumed);
    const rawFunctionalUnit = raw.get(_helpers_types__WEBPACK_IMPORTED_MODULE_2__.METRIC_KEY_MAP.functionalUnit);
    const energyConsumed = (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_3__.microjoulesToKWh)((_a = (type === 'Avg'
        ? (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_3__.getDeltaAverage)(rawEnergyConsumed)
        : (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_3__.getLatestValue)(rawEnergyConsumed))) !== null && _a !== void 0 ? _a : 0);
    const functionalUnit = (_b = (type === 'Avg'
        ? (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_3__.getAvgValue)(rawFunctionalUnit)
        : (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_3__.getLatestValue)(rawFunctionalUnit))) !== null && _b !== void 0 ? _b : 0;
    return {
        energyConsumed: Math.abs(energyConsumed),
        carbonIntensity,
        embodiedEmissions,
        functionalUnit
        // hepScore23
    };
}
function calculateSCI(sciValues) {
    const { E, I, M, R } = sciValues;
    const sci = R > 0 ? (E * I + M) / R : 0;
    // Example extra KPIs:
    // const sciPerUnit = R > 0 ? sci / R : 0;
    const energyPerUnit = (R > 0 ? E / R : 0) * 1000; // Convert kWh to Wh
    const operationalEmissions = E * I;
    return {
        sci,
        // hepScore23,
        // sciPerUnit,
        energyPerUnit,
        operationalEmissions
    };
}
async function calculateKPIs(rawMetrics) {
    const { energyConsumed: E, carbonIntensity: I, embodiedEmissions: M, functionalUnit: R
    // hepScore23
     } = await prometheusMetricsProxy('Avg', rawMetrics);
    // eslint-disable-next-line prettier/prettier
    const { sci, energyPerUnit, operationalEmissions } = calculateSCI({
        E,
        I,
        M,
        R
    });
    return {
        sci,
        // hepScore23,
        // sciPerUnit,
        energyPerUnit,
        operationalEmissions
    };
}
// const START = 1748855616000;
// const END = 1748858436000;
const kpiCardsData = [
    {
        key: 'sci',
        title: 'SCI',
        unit: 'gCO₂/unit',
        color: _helpers_constants__WEBPACK_IMPORTED_MODULE_4__.mainColour01,
        icon: (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_EnergySavingsLeafOutlined__WEBPACK_IMPORTED_MODULE_5__["default"], { sx: { fontSize: '56px', '& path': { fill: _helpers_constants__WEBPACK_IMPORTED_MODULE_4__.mainColour01 } } })),
        tempValue: 1.23
    },
    {
        key: 'operationalEmissions',
        title: 'Op. Emissions',
        unit: 'gCO₂',
        color: _helpers_constants__WEBPACK_IMPORTED_MODULE_4__.mainColour02,
        icon: (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_BoltOutlined__WEBPACK_IMPORTED_MODULE_6__["default"], { sx: { fontSize: '56px', '& path': { fill: _helpers_constants__WEBPACK_IMPORTED_MODULE_4__.mainColour02 } } })),
        tempValue: 3.33
    },
    {
        key: 'energyPerUnit',
        title: 'Energy/U',
        unit: 'Wh/unit',
        color: _helpers_constants__WEBPACK_IMPORTED_MODULE_4__.mainColour03,
        icon: (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_SolarPowerOutlined__WEBPACK_IMPORTED_MODULE_7__["default"], { sx: { fontSize: '56px', '& path': { fill: _helpers_constants__WEBPACK_IMPORTED_MODULE_4__.mainColour03 } } })),
        tempValue: 12.54
    }
];
const KPIComponent = ({ rawMetrics, experimentList, workflowList, handleRefreshExperimentList, selectedExperiment, setSelectedExperiment, selectedWorkflow, setSelectedWorkflow, handleSubmitExport }) => {
    const [kpi, setKpi] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(null);
    console.log(kpi);
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        let isMounted = true;
        calculateKPIs(rawMetrics).then(result => {
            if (isMounted) {
                setKpi(result);
            }
        });
        return () => {
            isMounted = false;
        };
    }, [rawMetrics]);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { width: '100%' } },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Stack, { direction: "row", sx: {
                px: 2,
                pb: 2,
                gap: 2,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-end'
            } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Box, { gap: 2, sx: _pages_WelcomePage__WEBPACK_IMPORTED_MODULE_8__.styles.buttonGrid },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton, { onClick: handleRefreshExperimentList },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_RefreshRounded__WEBPACK_IMPORTED_MODULE_9__["default"], null)),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.FormControl, null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputLabel, { sx: { background: 'white' } }, "Selected Workflow ID"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Select, { key: selectedWorkflow || 'workflow-select', size: "small", value: selectedWorkflow || '', onChange: e => {
                            var _a;
                            e !== null && setSelectedWorkflow((_a = e.target.value) !== null && _a !== void 0 ? _a : '');
                        }, sx: { minWidth: '150px' } },
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.MenuItem, { disabled: true, value: "" },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("em", null, "Select Workflow")),
                        workflowList &&
                            workflowList.map((workflowId, index) => {
                                return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.MenuItem, { key: index, value: workflowId }, workflowId));
                            }))),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.FormControl, null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputLabel, { sx: { background: 'white' } }, "Selected Experiment ID"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Select, { key: selectedExperiment || 'experiment-select', size: "small", value: selectedExperiment || '', onChange: e => {
                            var _a;
                            e !== null && setSelectedExperiment((_a = e.target.value) !== null && _a !== void 0 ? _a : '');
                        }, sx: { minWidth: '150px' } },
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.MenuItem, { disabled: true, value: "" },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("em", null, "Select Experiment")),
                        experimentList &&
                            experimentList.map((experimentId, index) => {
                                var _a;
                                return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.MenuItem, { key: index, value: experimentId }, (_a = experimentId.match(/\d{4}-\d{2}-\d{2} \d{2}:\d{2}/)) === null || _a === void 0 ? void 0 : _a[0]));
                            })))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Box, { sx: _pages_WelcomePage__WEBPACK_IMPORTED_MODULE_8__.styles.buttonGrid },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Button, { variant: "outlined", onClick: handleSubmitExport }, "Submit Experiment metadata to API"))),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Stack, { direction: "row", gap: 2 }, kpiCardsData.map(props => {
            return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_KpiValue__WEBPACK_IMPORTED_MODULE_10__["default"], { title: props.title, 
                // value={kpi?.[props.key] ?? 0}
                value: props.tempValue, unit: props.unit, color: props.color, Icon: props.icon }));
        }))));
};


/***/ }),

/***/ "./lib/components/KpiValue.js":
/*!************************************!*\
  !*** ./lib/components/KpiValue.js ***!
  \************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ KpiValue)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _helpers_utils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../helpers/utils */ "./lib/helpers/utils.js");



const styles = {
    paperKpi: {
        height: '300px',
        width: '100%',
        border: '1px solid #ccc',
        borderRadius: '10px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center'
    },
    typographyTitle: {
        fontSize: '32px',
        textAlign: 'center'
    },
    typographyValue: {
        fontWeight: 'bold',
        fontSize: '46px'
    },
    typographyUnit: {
        fontSize: '22px'
    }
};
function KpiValue(props) {
    const { Icon, value, unit, color, title, children } = props;
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { size: "grow", sx: { color } },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Paper, { elevation: 0, sx: {
                ...styles.paperKpi,
                border: `1px solid ${color}`
            } },
            Icon,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { sx: { ...styles.typographyTitle, color } }, title),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { sx: { ...styles.typographyValue, color } }, (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_2__.shortenNumber)(value)),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { sx: { ...styles.typographyUnit, color } }, unit),
            children)));
}


/***/ }),

/***/ "./lib/components/MetricSelector.js":
/*!******************************************!*\
  !*** ./lib/components/MetricSelector.js ***!
  \******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ MetricSelector)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);


function MetricSelector({ selectedMetric, setSelectedMetric, metrics }) {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.FormControl, { variant: "outlined", size: "small", style: { margin: 16, minWidth: 200 } },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.InputLabel, { id: "metric-label" }, "Metric"),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Select, { labelId: "metric-label", value: selectedMetric, label: "Metric", onChange: e => setSelectedMetric(e.target.value), size: "small" }, metrics.map(metric => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.MenuItem, { key: metric, value: metric }, metric))))));
}


/***/ }),

/***/ "./lib/components/NumberInput.js":
/*!***************************************!*\
  !*** ./lib/components/NumberInput.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ NumberInput)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _helpers_constants__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../helpers/constants */ "./lib/helpers/constants.js");



function NumberInput({ 
// currentRefreshValue,
handleRefreshNumberChange }) {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.TextField, { id: "outlined-number", label: "Refresh(S)", type: "number", slotProps: {
            inputLabel: {
                shrink: true
            }
        }, onChange: event => handleRefreshNumberChange(event.target.value), defaultValue: _helpers_constants__WEBPACK_IMPORTED_MODULE_2__.DEFAULT_REFRESH_RATE, size: "small", sx: { maxWidth: 90 } }));
}


/***/ }),

/***/ "./lib/components/RefreshButton.js":
/*!*****************************************!*\
  !*** ./lib/components/RefreshButton.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ RefreshButton)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_icons_material_RefreshRounded__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/icons-material/RefreshRounded */ "./node_modules/@mui/icons-material/esm/RefreshRounded.js");



function RefreshButton({ handleRefreshClick }) {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton, { onClick: handleRefreshClick, size: "small" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_RefreshRounded__WEBPACK_IMPORTED_MODULE_2__["default"], null))));
}


/***/ }),

/***/ "./lib/components/ScaphChart.js":
/*!**************************************!*\
  !*** ./lib/components/ScaphChart.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ TimeSeriesLineChart)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _visx_scale__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @visx/scale */ "webpack/sharing/consume/default/@visx/scale/@visx/scale?1592");
/* harmony import */ var _visx_scale__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_visx_scale__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _visx_shape__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @visx/shape */ "webpack/sharing/consume/default/@visx/shape/@visx/shape?7338");
/* harmony import */ var _visx_shape__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_visx_shape__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _visx_axis__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @visx/axis */ "webpack/sharing/consume/default/@visx/axis/@visx/axis");
/* harmony import */ var _visx_axis__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_visx_axis__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _visx_group__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! @visx/group */ "./node_modules/@visx/group/esm/Group.js");
/* harmony import */ var _visx_tooltip__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @visx/tooltip */ "webpack/sharing/consume/default/@visx/tooltip/@visx/tooltip");
/* harmony import */ var _visx_tooltip__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_visx_tooltip__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _visx_event__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @visx/event */ "webpack/sharing/consume/default/@visx/event/@visx/event");
/* harmony import */ var _visx_event__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_visx_event__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var d3_array__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! d3-array */ "./node_modules/d3-array/src/bisector.js");
/* harmony import */ var d3_array__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! d3-array */ "./node_modules/d3-array/src/extent.js");
/* harmony import */ var d3_array__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! d3-array */ "./node_modules/d3-array/src/min.js");
/* harmony import */ var d3_array__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! d3-array */ "./node_modules/d3-array/src/max.js");
/* harmony import */ var _helpers_utils__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../helpers/utils */ "./lib/helpers/utils.js");









const margin = { top: 20, right: 30, bottom: 40, left: 60 };
const width = 400;
const height = 300;
const bisectDate = (0,d3_array__WEBPACK_IMPORTED_MODULE_6__["default"])(d => d.date).left;
function TimeSeriesLineChart({ rawData }) {
    var _a, _b;
    const [data, setData] = react__WEBPACK_IMPORTED_MODULE_0___default().useState([]);
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        const data = (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_7__.downSample)((0,_helpers_utils__WEBPACK_IMPORTED_MODULE_7__.parseData)(rawData));
        setData(data);
    }, [rawData]);
    const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } = (0,_visx_tooltip__WEBPACK_IMPORTED_MODULE_4__.useTooltip)();
    const { containerRef, TooltipInPortal } = (0,_visx_tooltip__WEBPACK_IMPORTED_MODULE_4__.useTooltipInPortal)();
    function handleTooltip(event) {
        const { x: xPoint } = (0,_visx_event__WEBPACK_IMPORTED_MODULE_5__.localPoint)(event) || { x: 0 };
        const x0 = xScale.invert(xPoint);
        const index = bisectDate(data, x0, 1);
        const d0 = data[index - 1];
        const d1 = data[index];
        let d = d0;
        if (d1 && d0) {
            d =
                x0.getTime() - d0.date.getTime() > d1.date.getTime() - x0.getTime()
                    ? d1
                    : d0;
        }
        showTooltip({
            tooltipData: d,
            tooltipLeft: xScale(d.date),
            tooltipTop: yScale(d.value)
        });
    }
    const x = (d) => d.date;
    const y = (d) => d.value;
    const xExtent = (0,d3_array__WEBPACK_IMPORTED_MODULE_8__["default"])(data, x);
    const xDomain = xExtent[0] && xExtent[1]
        ? [xExtent[0], xExtent[1]]
        : [new Date(), new Date()];
    const xScale = (0,_visx_scale__WEBPACK_IMPORTED_MODULE_1__.scaleTime)({
        domain: xDomain,
        range: [margin.left, width - margin.right]
    });
    const yMin = (_a = (0,d3_array__WEBPACK_IMPORTED_MODULE_9__["default"])(data, y)) !== null && _a !== void 0 ? _a : 0;
    const yMax = (_b = (0,d3_array__WEBPACK_IMPORTED_MODULE_10__["default"])(data, y)) !== null && _b !== void 0 ? _b : 0;
    const yBuffer = (yMax - yMin) * 0.1; // 10% buffer
    const baseline = Math.max(0, yMin - yBuffer);
    const yScale = (0,_visx_scale__WEBPACK_IMPORTED_MODULE_1__.scaleLinear)({
        domain: [baseline, yMax],
        nice: true,
        range: [height - margin.bottom, margin.top]
    });
    const TooltipPortal = ({ tooltipData }) => TooltipInPortal({
        top: tooltipTop,
        left: tooltipLeft,
        style: {
            backgroundColor: 'white',
            color: '#1976d2',
            border: '1px solid #1976d2',
            padding: '6px 10px',
            borderRadius: 4,
            fontSize: 13,
            boxShadow: '0 1px 4px rgba(0,0,0,0.12)',
            maxWidth: '80px'
        },
        children: (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("strong", null, (tooltipData === null || tooltipData === void 0 ? void 0 : tooltipData.value) ? (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_7__.shortNumber)(tooltipData === null || tooltipData === void 0 ? void 0 : tooltipData.value) : 'N/A')),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { style: { fontSize: 11, color: '#333' } }, tooltipData === null || tooltipData === void 0 ? void 0 : tooltipData.date.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            }))))
    });
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { ref: containerRef, style: { position: 'relative' } },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("svg", { width: width, height: height },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_visx_group__WEBPACK_IMPORTED_MODULE_11__["default"], null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_visx_shape__WEBPACK_IMPORTED_MODULE_2__.LinePath, { data: data, x: d => xScale(x(d)), y: d => yScale(y(d)), stroke: "#1976d2", strokeWidth: 2 })),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_visx_axis__WEBPACK_IMPORTED_MODULE_3__.AxisLeft, { scale: yScale, top: 0, left: margin.left, 
                // label="Value"
                tickFormat: v => (0,_helpers_utils__WEBPACK_IMPORTED_MODULE_7__.shortNumber)(Number(v)), stroke: "#888", tickStroke: "#888", tickLabelProps: () => ({
                    fill: '#333',
                    fontSize: 12,
                    textAnchor: 'end',
                    dx: '-0.25em',
                    dy: '0.25em'
                }) }),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_visx_axis__WEBPACK_IMPORTED_MODULE_3__.AxisBottom, { scale: xScale, top: height - margin.bottom, left: 0, label: "Time", numTicks: 6, tickFormat: date => date instanceof Date
                    ? date.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                    })
                    : new Date(Number(date)).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                    }), stroke: "#888", tickStroke: "#888", tickLabelProps: () => ({
                    fill: '#333',
                    fontSize: 12,
                    textAnchor: 'middle'
                }) }),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("rect", { width: width - margin.left - margin.right, height: height - margin.top - margin.bottom, fill: "transparent", rx: 14, x: margin.left, y: margin.top, onMouseMove: handleTooltip, onMouseLeave: hideTooltip }),
            tooltipData ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("g", null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("circle", { cx: tooltipLeft, cy: tooltipTop, r: 5, fill: "#1976d2", stroke: "#fff", strokeWidth: 2, pointerEvents: "none" }))) : null),
        tooltipData ? TooltipPortal({ tooltipData }) : null));
}


/***/ }),

/***/ "./lib/components/SelectComponent.js":
/*!*******************************************!*\
  !*** ./lib/components/SelectComponent.js ***!
  \*******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ MultipleSelectCheckmarks)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_OutlinedInput__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/material/OutlinedInput */ "./node_modules/@mui/material/OutlinedInput/OutlinedInput.js");
/* harmony import */ var _mui_material_MenuItem__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @mui/material/MenuItem */ "./node_modules/@mui/material/MenuItem/MenuItem.js");
/* harmony import */ var _mui_material_FormControl__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material/FormControl */ "./node_modules/@mui/material/FormControl/FormControl.js");
/* harmony import */ var _mui_material_ListItemText__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @mui/material/ListItemText */ "./node_modules/@mui/material/ListItemText/ListItemText.js");
/* harmony import */ var _mui_material_Select__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/material/Select */ "./node_modules/@mui/material/Select/Select.js");
/* harmony import */ var _mui_material_Checkbox__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @mui/material/Checkbox */ "./node_modules/@mui/material/Checkbox/Checkbox.js");
/* harmony import */ var _helpers_constants__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../helpers/constants */ "./lib/helpers/constants.js");








const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
            width: 250
        }
    }
};
const metrics = [
    'CPU Usage',
    'CPU Time',
    'CPU Frequency',
    'Memory Energy',
    'Memory Used',
    'Network I/O',
    'Network Connections'
];
const noMetricSelected = 'No metric selected';
function MultipleSelectCheckmarks() {
    const [metricName, setMetricName] = react__WEBPACK_IMPORTED_MODULE_0__.useState([]);
    const handleChange = (event) => {
        const { target: { value } } = event;
        setMetricName(
        // On autofill we get a stringified value.
        typeof value === 'string' ? value.split(',') : value);
    };
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement("div", null,
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_FormControl__WEBPACK_IMPORTED_MODULE_1__["default"], { sx: { width: '100%' } },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Select__WEBPACK_IMPORTED_MODULE_2__["default"], { labelId: "metrics-multiple-checkbox-label", id: "metrics-multiple-checkbox", multiple: true, value: metricName, onChange: handleChange, input: react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_OutlinedInput__WEBPACK_IMPORTED_MODULE_3__["default"], { label: "Metric", sx: { width: '100%' } }), renderValue: selected => {
                    if (selected.length === 0) {
                        return react__WEBPACK_IMPORTED_MODULE_0__.createElement("em", null, noMetricSelected);
                    }
                    return selected.join(', ');
                }, MenuProps: MenuProps, size: "small", name: _helpers_constants__WEBPACK_IMPORTED_MODULE_4__.METRICS_GRAFANA_KEY },
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_MenuItem__WEBPACK_IMPORTED_MODULE_5__["default"], { disabled: true, value: "" },
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement("em", null, noMetricSelected)),
                metrics.map(metric => (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_MenuItem__WEBPACK_IMPORTED_MODULE_5__["default"], { key: metric, value: metric },
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Checkbox__WEBPACK_IMPORTED_MODULE_6__["default"], { checked: metricName.includes(metric) }),
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_ListItemText__WEBPACK_IMPORTED_MODULE_7__["default"], { primary: metric }))))),
            metricName.length > 0
                ? `${metricName.length} metric${metricName.length > 1 ? 's' : ''} selected.`
                : null)));
}


/***/ }),

/***/ "./lib/components/TabPaper.js":
/*!************************************!*\
  !*** ./lib/components/TabPaper.js ***!
  \************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ TabPaperDashboard)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_Tabs__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/material/Tabs */ "./node_modules/@mui/material/Tabs/Tabs.js");
/* harmony import */ var _mui_material_Tab__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/material/Tab */ "./node_modules/@mui/material/Tab/Tab.js");
/* harmony import */ var _mui_material_Box__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material/Box */ "./node_modules/@mui/material/Box/Box.js");
/* harmony import */ var _mui_icons_material_TimelineRounded__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/icons-material/TimelineRounded */ "./node_modules/@mui/icons-material/esm/TimelineRounded.js");
/* harmony import */ var _mui_icons_material_QueryStatsRounded__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @mui/icons-material/QueryStatsRounded */ "./node_modules/@mui/icons-material/esm/QueryStatsRounded.js");
/* harmony import */ var _mui_icons_material_HistoryRounded__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @mui/icons-material/HistoryRounded */ "./node_modules/@mui/icons-material/esm/HistoryRounded.js");







function CustomTabPanel(props) {
    const { children, value, index, ...other } = props;
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement("div", { role: "tabpanel", hidden: value !== index, id: `simple-tabpanel-${index}`, "aria-labelledby": `simple-tab-${index}`, ...other }, value === index && react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Box__WEBPACK_IMPORTED_MODULE_1__["default"], { sx: { p: 3 } }, children)));
}
function a11yProps(index) {
    return {
        id: `simple-tab-${index}`,
        'aria-controls': `simple-tabpanel-${index}`
    };
}
function TabPaperDashboard(props) {
    const { children } = props;
    const [value, setValue] = react__WEBPACK_IMPORTED_MODULE_0__.useState(0);
    const handleChange = (_event, newValue) => {
        setValue(newValue);
    };
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Box__WEBPACK_IMPORTED_MODULE_1__["default"], { sx: { width: '100%' } },
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Box__WEBPACK_IMPORTED_MODULE_1__["default"], { sx: { borderBottom: 1, borderColor: 'divider' } },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Tabs__WEBPACK_IMPORTED_MODULE_2__["default"], { value: value, onChange: handleChange, "aria-label": "basic tabs example", variant: "fullWidth" },
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Tab__WEBPACK_IMPORTED_MODULE_3__["default"], { icon: react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_icons_material_TimelineRounded__WEBPACK_IMPORTED_MODULE_4__["default"], null), label: "Real-time Metrics", ...a11yProps(0), sx: { flex: 1 } }),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Tab__WEBPACK_IMPORTED_MODULE_3__["default"], { icon: react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_icons_material_QueryStatsRounded__WEBPACK_IMPORTED_MODULE_5__["default"], null), label: "Predictions", ...a11yProps(1), sx: { flex: 1 } }),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Tab__WEBPACK_IMPORTED_MODULE_3__["default"], { icon: react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_icons_material_HistoryRounded__WEBPACK_IMPORTED_MODULE_6__["default"], null), label: "History", ...a11yProps(2), sx: { flex: 1 } }))),
        children
            ? children.map((element, index) => {
                return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(CustomTabPanel, { value: value, index: index }, element));
            })
            : null));
}


/***/ }),

/***/ "./lib/components/VerticalLinearStepper.js":
/*!*************************************************!*\
  !*** ./lib/components/VerticalLinearStepper.js ***!
  \*************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ VerticalLinearStepper)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_Box__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @mui/material/Box */ "./node_modules/@mui/material/Box/Box.js");
/* harmony import */ var _mui_material_Stepper__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @mui/material/Stepper */ "./node_modules/@mui/material/Stepper/Stepper.js");
/* harmony import */ var _mui_material_Step__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @mui/material/Step */ "./node_modules/@mui/material/Step/Step.js");
/* harmony import */ var _mui_material_StepLabel__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @mui/material/StepLabel */ "./node_modules/@mui/material/StepLabel/StepLabel.js");
/* harmony import */ var _mui_material_StepContent__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @mui/material/StepContent */ "./node_modules/@mui/material/StepContent/StepContent.js");
/* harmony import */ var _mui_material_Button__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/material/Button */ "./node_modules/@mui/material/Button/Button.js");
/* harmony import */ var _mui_material_Paper__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! @mui/material/Paper */ "./node_modules/@mui/material/Paper/Paper.js");
/* harmony import */ var _mui_material_Typography__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/material/Typography */ "./node_modules/@mui/material/Typography/Typography.js");
/* harmony import */ var _progress_CircularWithValueLabel__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./progress/CircularWithValueLabel */ "./lib/components/progress/CircularWithValueLabel.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _table_CollapsibleTable__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./table/CollapsibleTable */ "./lib/components/table/CollapsibleTable.js");
/* harmony import */ var _progress_LinearProgress__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./progress/LinearProgress */ "./lib/components/progress/LinearProgress.js");













const steps = [
    {
        label: 'Approach'
    },
    {
        label: 'Fetch/compute',
        hasButtons: false
    },
    {
        label: 'Visualisation options'
    },
    {
        label: 'Deployment',
        hasButtons: false
    }
];
function StepOne() {
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, null,
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.FormControl, null,
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.RadioGroup, { "aria-labelledby": "demo-radio-buttons-group-label", defaultValue: "pre-compute", name: "radio-buttons-group" },
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.FormControlLabel, { value: "pre-compute", control: react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Radio, null), label: "Pre-Compute" }),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.FormControlLabel, { value: "sample", control: react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Radio, null), label: "Sample Computation" }),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.FormControlLabel, { value: "simulation-pred", control: react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Radio, null), label: "Simulation/Prediction" })))));
}
function StepTwo({ handleFinish, label }) {
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, null,
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Typography__WEBPACK_IMPORTED_MODULE_2__["default"], null, label),
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_progress_CircularWithValueLabel__WEBPACK_IMPORTED_MODULE_3__["default"], { onFinish: handleFinish })));
}
function StepThree() {
    return react__WEBPACK_IMPORTED_MODULE_0__.createElement("div", null);
}
function StepFour({ handleFinish, label }) {
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, null,
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Button__WEBPACK_IMPORTED_MODULE_4__["default"], { onClick: handleFinish, title: "Reset" })));
}
function ContentHandler({ step, triggerNextStep, handleLastStep }) {
    switch (step) {
        default:
        case 0:
            return react__WEBPACK_IMPORTED_MODULE_0__.createElement(StepOne, null);
        case 1:
            return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(StepTwo, { handleFinish: triggerNextStep, label: "Predicting results..." }));
        case 2:
            return react__WEBPACK_IMPORTED_MODULE_0__.createElement(StepThree, null);
        case 3:
            return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(StepFour, { handleFinish: handleLastStep, label: "Deploying application..." }));
    }
}
function VerticalLinearStepper() {
    const [activeStep, setActiveStep] = react__WEBPACK_IMPORTED_MODULE_0__.useState(0);
    const [complete, setComplete] = react__WEBPACK_IMPORTED_MODULE_0__.useState(false);
    const [checkedIndex, setCheckedIndex] = react__WEBPACK_IMPORTED_MODULE_0__.useState(null);
    const disableNextStepThree = activeStep === 2 && checkedIndex === null;
    const handleNext = () => {
        setActiveStep(prevActiveStep => prevActiveStep + 1);
    };
    const handleBack = () => {
        setActiveStep(prevActiveStep => prevActiveStep - (prevActiveStep === 2 ? 2 : 1));
    };
    const handleReset = () => {
        setActiveStep(0);
        setComplete(false);
    };
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { display: 'flex', width: '100%', height: '500px' } },
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, null,
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Stepper__WEBPACK_IMPORTED_MODULE_5__["default"], { activeStep: activeStep, orientation: "vertical" }, steps.map((step, index) => (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Step__WEBPACK_IMPORTED_MODULE_6__["default"], { key: step.label },
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_StepLabel__WEBPACK_IMPORTED_MODULE_7__["default"], { optional: index === steps.length - 1 ? (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Typography__WEBPACK_IMPORTED_MODULE_2__["default"], { variant: "caption" }, "Last step")) : null }, step.label),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_StepContent__WEBPACK_IMPORTED_MODULE_8__["default"], null,
                    react__WEBPACK_IMPORTED_MODULE_0__.createElement(ContentHandler, { step: activeStep, triggerNextStep: handleNext, handleLastStep: handleReset }),
                    step.hasButtons !== false && (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Box__WEBPACK_IMPORTED_MODULE_9__["default"], { sx: { mb: 2 } },
                        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Button__WEBPACK_IMPORTED_MODULE_4__["default"], { variant: "contained", onClick: handleNext, sx: { mt: 1, mr: 1 }, disabled: disableNextStepThree }, index === steps.length - 1 ? 'Finish' : 'Continue'),
                        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Button__WEBPACK_IMPORTED_MODULE_4__["default"], { disabled: index === 0, onClick: handleBack, sx: { mt: 1, mr: 1 } }, "Back"))))))))),
        activeStep === 2 && (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Paper__WEBPACK_IMPORTED_MODULE_10__["default"], { square: true, elevation: 0, sx: { p: 3, width: '100%', overflow: 'visible' } },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_table_CollapsibleTable__WEBPACK_IMPORTED_MODULE_11__["default"], { checkedIndex: checkedIndex, setCheckedIndex: setCheckedIndex }))),
        activeStep === 3 && (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { width: '400px' } }, complete ? (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { display: 'flex', justifyContent: 'center' } },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Typography__WEBPACK_IMPORTED_MODULE_2__["default"], null, "Deployment complete!"),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Button__WEBPACK_IMPORTED_MODULE_4__["default"], { title: "Reset", onClick: handleReset }))) : (react__WEBPACK_IMPORTED_MODULE_0__.createElement(react__WEBPACK_IMPORTED_MODULE_0__.Fragment, null,
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Typography__WEBPACK_IMPORTED_MODULE_2__["default"], null, "Deploying..."),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_progress_LinearProgress__WEBPACK_IMPORTED_MODULE_12__["default"], { setComplete: () => setComplete(true) })))))));
}


/***/ }),

/***/ "./lib/components/progress/CircularWithValueLabel.js":
/*!***********************************************************!*\
  !*** ./lib/components/progress/CircularWithValueLabel.js ***!
  \***********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ CircularWithValueLabel)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_CircularProgress__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/material/CircularProgress */ "./node_modules/@mui/material/CircularProgress/CircularProgress.js");
/* harmony import */ var _mui_material_Typography__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/material/Typography */ "./node_modules/@mui/material/Typography/Typography.js");
/* harmony import */ var _mui_material_Box__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material/Box */ "./node_modules/@mui/material/Box/Box.js");




function CircularProgressWithLabel(props) {
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Box__WEBPACK_IMPORTED_MODULE_1__["default"], { sx: { position: 'relative', display: 'inline-flex' } },
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_CircularProgress__WEBPACK_IMPORTED_MODULE_2__["default"], { variant: "determinate", ...props }),
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Box__WEBPACK_IMPORTED_MODULE_1__["default"], { sx: {
                top: 0,
                left: 0,
                bottom: 0,
                right: 0,
                position: 'absolute',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            } },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Typography__WEBPACK_IMPORTED_MODULE_3__["default"], { variant: "caption", component: "div", sx: { color: 'text.secondary' } }, `${Math.round(props.value)}%`))));
}
function CircularWithValueLabel({ onFinish }) {
    const [progress, setProgress] = react__WEBPACK_IMPORTED_MODULE_0__.useState(10);
    function handleConclusion() {
        onFinish();
        return 0;
    }
    react__WEBPACK_IMPORTED_MODULE_0__.useEffect(() => {
        const timer = setInterval(() => {
            setProgress(prevProgress => prevProgress >= 100 ? handleConclusion() : prevProgress + 10);
        }, 400);
        return () => {
            clearInterval(timer);
        };
    }, []);
    return react__WEBPACK_IMPORTED_MODULE_0__.createElement(CircularProgressWithLabel, { value: progress });
}


/***/ }),

/***/ "./lib/components/progress/LinearProgress.js":
/*!***************************************************!*\
  !*** ./lib/components/progress/LinearProgress.js ***!
  \***************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ LinearBuffer)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_Box__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material/Box */ "./node_modules/@mui/material/Box/Box.js");
/* harmony import */ var _mui_material_LinearProgress__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/material/LinearProgress */ "./node_modules/@mui/material/LinearProgress/LinearProgress.js");



function LinearBuffer({ setComplete }) {
    const [progress, setProgress] = react__WEBPACK_IMPORTED_MODULE_0__.useState(0);
    const [buffer, setBuffer] = react__WEBPACK_IMPORTED_MODULE_0__.useState(10);
    const progressRef = react__WEBPACK_IMPORTED_MODULE_0__.useRef(() => { });
    react__WEBPACK_IMPORTED_MODULE_0__.useEffect(() => {
        progressRef.current = () => {
            if (progress === 100) {
                setComplete();
            }
            else {
                setProgress(progress + 1);
                if (buffer < 100 && progress % 5 === 0) {
                    const newBuffer = buffer + 1 + Math.random() * 10;
                    setBuffer(newBuffer > 100 ? 100 : newBuffer);
                }
            }
        };
    });
    react__WEBPACK_IMPORTED_MODULE_0__.useEffect(() => {
        const timer = setInterval(() => {
            progressRef.current();
        }, 50);
        return () => {
            clearInterval(timer);
        };
    }, []);
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Box__WEBPACK_IMPORTED_MODULE_1__["default"], { sx: { width: '100%' } },
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_LinearProgress__WEBPACK_IMPORTED_MODULE_2__["default"], { variant: "buffer", value: progress, valueBuffer: buffer })));
}


/***/ }),

/***/ "./lib/components/table/CollapsibleTable.js":
/*!**************************************************!*\
  !*** ./lib/components/table/CollapsibleTable.js ***!
  \**************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ CollapsibleTable)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_Box__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @mui/material/Box */ "./node_modules/@mui/material/Box/Box.js");
/* harmony import */ var _mui_material_Collapse__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @mui/material/Collapse */ "./node_modules/@mui/material/Collapse/Collapse.js");
/* harmony import */ var _mui_material_IconButton__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @mui/material/IconButton */ "./node_modules/@mui/material/IconButton/IconButton.js");
/* harmony import */ var _mui_material_Table__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! @mui/material/Table */ "./node_modules/@mui/material/Table/Table.js");
/* harmony import */ var _mui_material_TableBody__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! @mui/material/TableBody */ "./node_modules/@mui/material/TableBody/TableBody.js");
/* harmony import */ var _mui_material_TableCell__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/material/TableCell */ "./node_modules/@mui/material/TableCell/TableCell.js");
/* harmony import */ var _mui_material_TableContainer__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! @mui/material/TableContainer */ "./node_modules/@mui/material/TableContainer/TableContainer.js");
/* harmony import */ var _mui_material_TableHead__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! @mui/material/TableHead */ "./node_modules/@mui/material/TableHead/TableHead.js");
/* harmony import */ var _mui_material_TableRow__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/material/TableRow */ "./node_modules/@mui/material/TableRow/TableRow.js");
/* harmony import */ var _mui_material_Typography__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/material/Typography */ "./node_modules/@mui/material/Typography/Typography.js");
/* harmony import */ var _mui_material_Paper__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! @mui/material/Paper */ "./node_modules/@mui/material/Paper/Paper.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_icons_material_KeyboardArrowDown__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @mui/icons-material/KeyboardArrowDown */ "./node_modules/@mui/icons-material/esm/KeyboardArrowDown.js");
/* harmony import */ var _mui_icons_material_KeyboardArrowUp__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @mui/icons-material/KeyboardArrowUp */ "./node_modules/@mui/icons-material/esm/KeyboardArrowUp.js");

// import PropTypes from 'prop-types';














function createData(sci, time, availability) {
    const datacentres = Array.from({ length: 2 }, (_, index) => ({
        label: `Data Centre ${index + 1}`,
        details: {
            cpu: {
                usage: Number((Math.random() * 100).toFixed(2)),
                time: Math.floor(Math.random() * 10000),
                frequency: Number((Math.random() * 3 + 2).toFixed(2))
            },
            memory: {
                energy: Number((Math.random() * 1000).toFixed(2)),
                used: Math.floor(Math.random() * 1000000)
            },
            network: {
                io: Number((Math.random() * 100).toFixed(2)),
                connections: Math.floor(Math.random() * 50)
            }
        }
    }));
    return { sci, time, availability, datacentres };
}
function Row({ row, checkedIndex, setSelectedIndex, rowIndex }) {
    const [open, setOpen] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableRow__WEBPACK_IMPORTED_MODULE_2__["default"], null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableCell__WEBPACK_IMPORTED_MODULE_3__["default"], null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { display: 'flex', alignItems: 'center' } },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Typography__WEBPACK_IMPORTED_MODULE_4__["default"], null, rowIndex),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_IconButton__WEBPACK_IMPORTED_MODULE_5__["default"], { "aria-label": "expand row", size: "small", onClick: () => setOpen(!open) }, open ? react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_KeyboardArrowUp__WEBPACK_IMPORTED_MODULE_6__["default"], null) : react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_KeyboardArrowDown__WEBPACK_IMPORTED_MODULE_7__["default"], null)),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Checkbox, { checked: checkedIndex, onClick: setSelectedIndex }))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableCell__WEBPACK_IMPORTED_MODULE_3__["default"], null, row.sci),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableCell__WEBPACK_IMPORTED_MODULE_3__["default"], { align: "right" }, row.time),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableCell__WEBPACK_IMPORTED_MODULE_3__["default"], { align: "center" }, row.availability)),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableRow__WEBPACK_IMPORTED_MODULE_2__["default"], null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableCell__WEBPACK_IMPORTED_MODULE_3__["default"], { style: { paddingBottom: 0, paddingTop: 0 }, colSpan: 4 },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Collapse__WEBPACK_IMPORTED_MODULE_8__["default"], { in: open, timeout: "auto", unmountOnExit: true },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Box__WEBPACK_IMPORTED_MODULE_9__["default"], { sx: { m: 1 } }, row.datacentres.map((datacentre, index) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Box__WEBPACK_IMPORTED_MODULE_9__["default"], { key: index, sx: {
                            mb: 2,
                            border: '1px solid #ddd',
                            borderRadius: '8px',
                            p: 2
                        } },
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Typography__WEBPACK_IMPORTED_MODULE_4__["default"], { sx: { fontWeight: 'bold', mb: 1 }, variant: "subtitle1" }, datacentre.label),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { container: true, spacing: 2, sx: { display: 'flex', justifyContent: 'space-between' } },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: {
                                    display: 'flex',
                                    flexDirection: 'column',
                                    flexGrow: 1
                                } },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Typography__WEBPACK_IMPORTED_MODULE_4__["default"], { sx: { fontWeight: 'bold' } }, "CPU"),
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("ul", { style: { paddingInlineStart: '10px' } },
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("li", null,
                                        "Usage: ",
                                        datacentre.details.cpu.usage,
                                        " %"),
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("li", null,
                                        "Time: ",
                                        datacentre.details.cpu.time,
                                        " \u03BCs"),
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("li", null,
                                        "Frequency: ",
                                        datacentre.details.cpu.frequency,
                                        " GHz"))),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: {
                                    display: 'flex',
                                    flexDirection: 'column',
                                    flexGrow: 1
                                } },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Typography__WEBPACK_IMPORTED_MODULE_4__["default"], { sx: { fontWeight: 'bold' } }, "Memory"),
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("ul", { style: { paddingInlineStart: '10px' } },
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("li", null,
                                        "Energy: ",
                                        datacentre.details.memory.energy,
                                        " \u03BCJ"),
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("li", null,
                                        "Used: ",
                                        datacentre.details.memory.used,
                                        " Bytes"))),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: {
                                    display: 'flex',
                                    flexDirection: 'column',
                                    flexGrow: 1
                                } },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Typography__WEBPACK_IMPORTED_MODULE_4__["default"], { sx: { fontWeight: 'bold' } }, "Network"),
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("ul", { style: { paddingInlineStart: '10px' } },
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("li", null,
                                        "IO: ",
                                        datacentre.details.network.io,
                                        " B/s"),
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement("li", null,
                                        "Connections: ",
                                        datacentre.details.network.connections)))))))))))));
}
const rows = [
    createData(12.33, 4500, '++'),
    createData(14.12, 5200, '+'),
    createData(10.89, 4300, '+++')
];
function CollapsibleTable({ checkedIndex, setCheckedIndex }) {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableContainer__WEBPACK_IMPORTED_MODULE_10__["default"], { component: _mui_material_Paper__WEBPACK_IMPORTED_MODULE_11__["default"] },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_Table__WEBPACK_IMPORTED_MODULE_12__["default"], { "aria-label": "collapsible table" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableHead__WEBPACK_IMPORTED_MODULE_13__["default"], null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableRow__WEBPACK_IMPORTED_MODULE_2__["default"], null,
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableCell__WEBPACK_IMPORTED_MODULE_3__["default"], null),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableCell__WEBPACK_IMPORTED_MODULE_3__["default"], null, "SCI"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableCell__WEBPACK_IMPORTED_MODULE_3__["default"], { align: "right" }, "Est. Time (s)"),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableCell__WEBPACK_IMPORTED_MODULE_3__["default"], { align: "center" }, "Availability"))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material_TableBody__WEBPACK_IMPORTED_MODULE_14__["default"], null, rows.map((row, index) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(Row, { key: index, row: row, rowIndex: index, checkedIndex: index === checkedIndex, setSelectedIndex: () => {
                    const newValue = index === checkedIndex ? null : index;
                    setCheckedIndex(newValue);
                } })))))));
}


/***/ }),

/***/ "./lib/dialog/CreateChartDialog.js":
/*!*****************************************!*\
  !*** ./lib/dialog/CreateChartDialog.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ CreateChartDialog)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_Button__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @mui/material/Button */ "./node_modules/@mui/material/Button/Button.js");
/* harmony import */ var _mui_material_TextField__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @mui/material/TextField */ "./node_modules/@mui/material/TextField/TextField.js");
/* harmony import */ var _mui_material_Dialog__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material/Dialog */ "./node_modules/@mui/material/Dialog/Dialog.js");
/* harmony import */ var _mui_material_DialogActions__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @mui/material/DialogActions */ "./node_modules/@mui/material/DialogActions/DialogActions.js");
/* harmony import */ var _mui_material_DialogContent__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/material/DialogContent */ "./node_modules/@mui/material/DialogContent/DialogContent.js");
/* harmony import */ var _mui_material_DialogContentText__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @mui/material/DialogContentText */ "./node_modules/@mui/material/DialogContentText/DialogContentText.js");
/* harmony import */ var _mui_material_DialogTitle__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/material/DialogTitle */ "./node_modules/@mui/material/DialogTitle/DialogTitle.js");
/* harmony import */ var _components_SelectComponent__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../components/SelectComponent */ "./lib/components/SelectComponent.js");
/* harmony import */ var _helpers_constants__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../helpers/constants */ "./lib/helpers/constants.js");










const isValidUrl = (urlString) => {
    const urlPattern = new RegExp('^(http?:\\/\\/)?' + // validate protocol
        '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + // validate domain name
        '((\\d{1,3}\\.){3}\\d{1,3}))' + // validate OR ip (v4) address
        '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // validate port and path
        '(\\?[;&a-z\\d%_.~+=-]*)?' + // validate query string
        '(\\#[-a-z\\d_]*)?$', 'i'); // validate fragment locator
    return !!urlPattern.test(urlString);
};
function CreateChartDialog({ open, handleClose, sendNewMetrics, sendNewUrl }) {
    return (react__WEBPACK_IMPORTED_MODULE_0__.createElement(react__WEBPACK_IMPORTED_MODULE_0__.Fragment, null,
        react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Dialog__WEBPACK_IMPORTED_MODULE_1__["default"], { open: open, onClose: (_e, reason) => {
                if (reason === 'backdropClick' || reason === 'escapeKeyDown') {
                    return;
                }
                else {
                    handleClose(true);
                }
            }, slotProps: {
                paper: {
                    component: 'form',
                    onSubmit: (event) => {
                        event.preventDefault();
                        const formData = new FormData(event.currentTarget);
                        const formJson = Object.fromEntries(formData.entries());
                        if (_helpers_constants__WEBPACK_IMPORTED_MODULE_2__.METRICS_GRAFANA_KEY in formJson) {
                            const metrics = formJson.metrics_grafana;
                            sendNewMetrics(metrics.split(','));
                        }
                        if (_helpers_constants__WEBPACK_IMPORTED_MODULE_2__.URL_GRAFANA_KEY in formJson) {
                            const url = formJson.url_grafana;
                            // Only send the URl if it is valid, since it is optional.
                            if (isValidUrl(url)) {
                                sendNewUrl(url);
                            }
                        }
                        else {
                            throw 'Some error happened with the form.';
                        }
                    }
                }
            } },
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_DialogTitle__WEBPACK_IMPORTED_MODULE_3__["default"], null, "Add Metric Chart"),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_DialogContent__WEBPACK_IMPORTED_MODULE_4__["default"], null,
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_DialogContentText__WEBPACK_IMPORTED_MODULE_5__["default"], null, "To create a chart, you must either select a metric from the list, and/or provide the URL from the Grafana's dashboard."),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_components_SelectComponent__WEBPACK_IMPORTED_MODULE_6__["default"], null),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_TextField__WEBPACK_IMPORTED_MODULE_7__["default"], { autoFocus: true, 
                    // required
                    margin: "dense", id: "name", name: _helpers_constants__WEBPACK_IMPORTED_MODULE_2__.URL_GRAFANA_KEY, label: "Grafana URL", type: "url", fullWidth: true, variant: "outlined", size: "small" })),
            react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_DialogActions__WEBPACK_IMPORTED_MODULE_8__["default"], null,
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Button__WEBPACK_IMPORTED_MODULE_9__["default"], { onClick: () => handleClose(true), sx: { textTransform: 'none' } }, "Cancel"),
                react__WEBPACK_IMPORTED_MODULE_0__.createElement(_mui_material_Button__WEBPACK_IMPORTED_MODULE_9__["default"], { type: "submit", sx: { textTransform: 'none' } }, "Create")))));
}


/***/ }),

/***/ "./lib/helpers/constants.js":
/*!**********************************!*\
  !*** ./lib/helpers/constants.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   CONTAINER_ID: () => (/* binding */ CONTAINER_ID),
/* harmony export */   DEFAULT_REFRESH_RATE: () => (/* binding */ DEFAULT_REFRESH_RATE),
/* harmony export */   METRICS_GRAFANA_KEY: () => (/* binding */ METRICS_GRAFANA_KEY),
/* harmony export */   NR_CHARTS: () => (/* binding */ NR_CHARTS),
/* harmony export */   URL_GRAFANA_KEY: () => (/* binding */ URL_GRAFANA_KEY),
/* harmony export */   end: () => (/* binding */ end),
/* harmony export */   endDateJs: () => (/* binding */ endDateJs),
/* harmony export */   mainColour01: () => (/* binding */ mainColour01),
/* harmony export */   mainColour02: () => (/* binding */ mainColour02),
/* harmony export */   mainColour03: () => (/* binding */ mainColour03),
/* harmony export */   start: () => (/* binding */ start),
/* harmony export */   startDateJs: () => (/* binding */ startDateJs)
/* harmony export */ });
/* harmony import */ var dayjs__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! dayjs */ "webpack/sharing/consume/default/dayjs/dayjs");
/* harmony import */ var dayjs__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(dayjs__WEBPACK_IMPORTED_MODULE_0__);

const CONTAINER_ID = 'main-container-id-scroll';
const DEFAULT_REFRESH_RATE = 2;
const URL_GRAFANA_KEY = 'url_grafana';
const METRICS_GRAFANA_KEY = 'metrics_grafana';
const NR_CHARTS = 4;
const end = Math.floor(Date.now() / 1000);
const start = end - 3600; // last hour
const endDateJs = dayjs__WEBPACK_IMPORTED_MODULE_0___default()(end * 1000);
const startDateJs = dayjs__WEBPACK_IMPORTED_MODULE_0___default()(start * 1000);
const mainColour01 = '#6B8E23';
const mainColour02 = '#A0522D';
const mainColour03 = '#4682B4';


/***/ }),

/***/ "./lib/helpers/types.js":
/*!******************************!*\
  !*** ./lib/helpers/types.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   METRIC_KEY_MAP: () => (/* binding */ METRIC_KEY_MAP)
/* harmony export */ });
const METRIC_KEY_MAP = {
    energyConsumed: 'scaph_host_energy_microjoules',
    carbonIntensity: 'scaph_carbon_intensity',
    embodiedEmissions: 'scaph_embodied_emissions',
    functionalUnit: 'scaph_host_load_avg_fifteen' // R (e.g., load avg as a proxy)
    //   hepScore23: 'scaph_hep_score_23' // HEPScore23 (if tracked)
};


/***/ }),

/***/ "./lib/helpers/utils.js":
/*!******************************!*\
  !*** ./lib/helpers/utils.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   downSample: () => (/* binding */ downSample),
/* harmony export */   getAvgValue: () => (/* binding */ getAvgValue),
/* harmony export */   getDeltaAverage: () => (/* binding */ getDeltaAverage),
/* harmony export */   getLatestValue: () => (/* binding */ getLatestValue),
/* harmony export */   getOffsetHours: () => (/* binding */ getOffsetHours),
/* harmony export */   joulesToKWh: () => (/* binding */ joulesToKWh),
/* harmony export */   microjoulesToJoules: () => (/* binding */ microjoulesToJoules),
/* harmony export */   microjoulesToKWh: () => (/* binding */ microjoulesToKWh),
/* harmony export */   parseData: () => (/* binding */ parseData),
/* harmony export */   shortNumber: () => (/* binding */ shortNumber),
/* harmony export */   shortenNumber: () => (/* binding */ shortenNumber),
/* harmony export */   toLowerCaseWithUnderscores: () => (/* binding */ toLowerCaseWithUnderscores)
/* harmony export */ });
// import dayjs from 'dayjs';
// Downsample: pick every Nth point to reduce chart density
function downSample(data, maxPoints = 250) {
    if (data.length <= maxPoints) {
        return data;
    }
    const step = Math.ceil(data.length / maxPoints);
    return data.filter((_, idx) => idx % step === 0);
}
const parseData = (data) => data.map(([timestamp, value]) => ({
    date: new Date(timestamp * 1000),
    value: Number(value)
}));
function shortNumber(num, digits = 3) {
    if (num === null || num === undefined) {
        return '';
    }
    const units = [
        { value: 1e12, symbol: 'T' },
        { value: 1e9, symbol: 'B' },
        { value: 1e6, symbol: 'M' },
        { value: 1e3, symbol: 'K' }
    ];
    for (const unit of units) {
        if (Math.abs(num) >= unit.value) {
            return ((num / unit.value).toFixed(digits).replace(/\.0+$/, '') + unit.symbol);
        }
    }
    return num.toString();
}
// Convert microjoules to joules
const microjoulesToJoules = (uj) => uj / 1000000;
// Convert joules to kWh
const joulesToKWh = (j) => j / 3600000;
function microjoulesToKWh(uj) {
    return uj / 1000000 / 3600000;
}
// export function getDateNow() {
//   return dayjs(new Date());
// }
function shortenNumber(num) {
    const units = ['', 'K', 'M', 'B', 'T'];
    let unitIndex = 0;
    // Make the number shorter with K/M/B...
    while (num >= 1000 && unitIndex < units.length - 1) {
        num /= 1000;
        unitIndex++;
    }
    // Determine precision based on the value
    let rounded;
    if (num < 1) {
        rounded = num.toFixed(3); // Show up to 3 decimal places if < 1
    }
    else {
        rounded = (Math.floor(num * 10) / 10).toString(); // 1 decimal place for >= 1
    }
    return `${rounded}${units[unitIndex]}`;
}
function getDeltaAverage(metricData) {
    if (!metricData || metricData.length < 2) {
        return undefined;
    }
    // Sort by timestamp ascending to calculate deltas
    const sorted = [...metricData].sort((a, b) => a[0] - b[0]);
    let totalDelta = 0;
    for (let i = 1; i < sorted.length; i++) {
        const [prevTime, prevValue] = sorted[i - 1];
        const [currTime, currValue] = sorted[i];
        const deltaValue = parseFloat(currValue) - parseFloat(prevValue);
        const deltaTime = (currTime - prevTime) / 1000; // convert ms to seconds
        if (deltaValue >= 0 && deltaTime > 0) {
            totalDelta += deltaValue;
        }
    }
    return totalDelta / sorted.length || undefined;
}
function getLatestValue(metricData) {
    if (!metricData || metricData.length === 0) {
        return null;
    }
    // Sort by timestamp descending and pick the first
    const latest = metricData.reduce((max, curr) => (curr[0] > max[0] ? curr : max), metricData[0]);
    return parseFloat(latest[1]);
}
function getAvgValue(metricData) {
    if (!metricData || metricData.length === 0) {
        return undefined;
    }
    const sum = metricData.reduce((acc, [, value]) => acc + parseFloat(value), 0);
    return sum / metricData.length;
}
function getOffsetHours() {
    const offsetMinutes = new Date().getTimezoneOffset();
    const offsetHours = -offsetMinutes / 60;
    return offsetHours;
}
function toLowerCaseWithUnderscores(input) {
    const formatted = input.toLowerCase().replace(/\s+/g, '_');
    return formatted;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _widget__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./widget */ "./lib/widget.js");
/* harmony import */ var _api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./api/handleNotebookContents */ "./lib/api/handleNotebookContents.js");
/* harmony import */ var _api_apiScripts__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./api/apiScripts */ "./lib/api/apiScripts.js");
// import React from 'react';






// import JupyterDialogWarning from './components/JupyterDialogWarning';
// import { monitorCellExecutions } from './api/monitorCellExecutions';
/**
 * Main reference: https://github.com/jupyterlab/extension-examples/blob/71486d7b891175fb3883a8b136b8edd2cd560385/react/react-widget/src/index.ts
 * And all other files in the repo.
 */
const namespaceId = 'gdapod';
/**
 * Initialization data for the GreenDIGIT JupyterLab extension.
 */
const plugin = {
    id: 'ecojupyter',
    description: 'GreenDIGIT EcoJupyter App',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ICommandPalette, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.INotebookTracker],
    activate: async (app, palette, restorer, notebookTracker) => {
        var _a;
        // const [currentPanel, setCurrentPanel] = React.useState<NotebookPanel | null>(null);
        const { shell } = app;
        // Create a widget tracker
        const tracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.WidgetTracker({
            namespace: namespaceId
        });
        // Ensure the tracker is restored properly on refresh
        restorer === null || restorer === void 0 ? void 0 : restorer.restore(tracker, {
            command: `${namespaceId}:open`,
            name: () => 'gd-ecojupyter'
            // when: app.restored, // Ensure restorer waits for the app to be fully restored
        });
        // Define a widget creator function
        const newWidget = async (username, panel) => {
            const content = new _widget__WEBPACK_IMPORTED_MODULE_3__.MainWidget(username, panel);
            const widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.MainAreaWidget({ content });
            widget.id = 'gd-ecojupyter';
            widget.title.label = 'GreenDIGIT EcoJupyter Dashboard';
            widget.title.closable = true;
            return widget;
        };
        // Add an application command
        const openCommand = `${namespaceId}:open`;
        async function addNewWidget(shell, widget, username, panel) {
            // If the widget is not provided or is disposed, create a new one
            if (!widget || widget.isDisposed) {
                widget = await newWidget(username, panel);
                // Add the widget to the tracker and shell
                tracker.add(widget);
                shell.add(widget, 'main');
            }
            if (!widget.isAttached) {
                shell.add(widget, 'main');
            }
            shell.activateById(widget.id);
        }
        app.commands.addCommand(openCommand, {
            label: 'Open GreenDIGIT Dashboard',
            execute: async () => {
                var _a;
                const panel = notebookTracker.currentWidget;
                if (!panel) {
                    return;
                }
                await panel.context.ready;
                try {
                    const username = (_a = (await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_4__.handleNotebookSessionContents)(panel, _api_apiScripts__WEBPACK_IMPORTED_MODULE_5__.getUsernameSh))) !== null && _a !== void 0 ? _a : '';
                    await addNewWidget(shell, tracker.currentWidget, username, panel);
                }
                catch (err) {
                    console.error('Failed to fetch username:', err);
                }
            }
        });
        // app.restored.then(() => {
        //   JupyterDialogWarning({
        //     message:
        //       'EcoJupyter has been installed. Please reload the window to activate it.',
        //     buttonLabel: 'Reload window',
        //     action: () => window.location.reload()
        //   });
        // });
        // Add the command to the palette
        palette.addItem({
            command: openCommand,
            category: 'Sustainability metrics'
        });
        // Restore the widget if available
        if (!tracker.currentWidget) {
            const panel = notebookTracker.currentWidget;
            let username = null;
            if (panel) {
                await panel.context.ready;
                try {
                    username =
                        (_a = (await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_4__.handleNotebookSessionContents)(panel, _api_apiScripts__WEBPACK_IMPORTED_MODULE_5__.getUsernameSh))) !== null && _a !== void 0 ? _a : null;
                }
                catch (err) {
                    console.warn('Could not fetch username during restore, using default:', err);
                }
            }
            if (username !== null && panel !== null) {
                const widget = await newWidget(username, panel);
                tracker.add(widget);
                shell.add(widget, 'main');
            }
        }
        const seenKey = 'greendigit-ecojupyter-seen';
        const seen = window.sessionStorage.getItem(seenKey);
        if (seen) {
            const panel = notebookTracker.currentWidget;
            if (panel) {
                await panel.context.ready;
                try {
                    const username = await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_4__.handleNotebookSessionContents)(panel, _api_apiScripts__WEBPACK_IMPORTED_MODULE_5__.getUsernameSh);
                    if (username) {
                        await addNewWidget(shell, tracker.currentWidget, username, panel);
                    }
                }
                catch (err) {
                    console.error('Failed to fetch username on seen restore:', err);
                }
            }
        }
        notebookTracker.widgetAdded.connect((_, panel) => {
            panel.context.ready.then(async () => {
                var _a;
                // Saving username
                await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_4__.handleNotebookSessionContents)(panel, _api_apiScripts__WEBPACK_IMPORTED_MODULE_5__.saveUsernameSh);
                const username = (_a = (await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_4__.handleNotebookSessionContents)(panel, _api_apiScripts__WEBPACK_IMPORTED_MODULE_5__.getUsernameSh))) !== null && _a !== void 0 ? _a : '';
                await addNewWidget(shell, tracker.currentWidget, username, panel);
                _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.NotebookActions.executed.connect(async (_, args) => {
                    const { cell, notebook } = args;
                    const index = notebook.widgets.indexOf(cell);
                    const isFirst = index === 0;
                    const isLast = index === notebook.widgets.length - 1;
                    if (isFirst) {
                        await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_4__.handleFirstCellExecution)(panel);
                    }
                    if (isLast) {
                        await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_4__.handleLastCellExecution)(panel);
                    }
                });
                // Monitor cell execution
                // monitorCellExecutions(panel);
            });
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/pages/ChartsPage.js":
/*!*********************************!*\
  !*** ./lib/pages/ChartsPage.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ ChartsPage)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _components_AddButton__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../components/AddButton */ "./lib/components/AddButton.js");
/* harmony import */ var _dialog_CreateChartDialog__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../dialog/CreateChartDialog */ "./lib/dialog/CreateChartDialog.js");
/* harmony import */ var _components_ChartWrapper__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components/ChartWrapper */ "./lib/components/ChartWrapper.js");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_GoBackButton__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../components/GoBackButton */ "./lib/components/GoBackButton.js");






const CONFIG_BASE_URL = 'http://localhost:3000/';
const DEFAULT_SRC_IFRAME = `${CONFIG_BASE_URL}d-solo/behmsglt2r08wa/memory-and-cpu?orgId=1&from=1743616284487&to=1743621999133&timezone=browser&theme=light&panelId=1&__feature.dashboardSceneSolo`;
function ChartsPage({ handleGoBack }) {
    const [iframeMap, setIFrameMap] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(new Map());
    const [createChartOpen, setCreateChartOpen] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    function handleDeleteIFrame(keyId) {
        setIFrameMap(prevMap => {
            const newMap = new Map(prevMap);
            newMap === null || newMap === void 0 ? void 0 : newMap.delete(keyId);
            return newMap;
        });
    }
    function createIFrame({ src, height, width, keyId }) {
        return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_ChartWrapper__WEBPACK_IMPORTED_MODULE_2__["default"], { keyId: keyId, src: src, width: width, height: height, onDelete: handleDeleteIFrame }));
    }
    function createChart(newUrl) {
        const newKeyId = Number(String(Date.now()) + String(Math.round(Math.random() * 10000)));
        const iframe = createIFrame({
            src: newUrl !== null && newUrl !== void 0 ? newUrl : DEFAULT_SRC_IFRAME,
            height: 400,
            width: 600,
            keyId: newKeyId
        });
        return [newKeyId, iframe];
    }
    function handleOpenCreateChartDialog() {
        setCreateChartOpen(true);
    }
    function handleNewMetrics(newMetrics) {
        const newMap = new Map(iframeMap);
        for (let i = 0; i < newMetrics.length; i++) {
            newMap.set(...createChart(DEFAULT_SRC_IFRAME));
        }
        setIFrameMap(newMap);
        setCreateChartOpen(false);
    }
    function handleSubmitUrl(newUrl) {
        const newMap = new Map(iframeMap);
        newMap.set(...createChart(newUrl));
        // setIFrameMap(newMap);
    }
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { display: 'flex', flexDirection: 'column' } },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { display: 'flex' } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_GoBackButton__WEBPACK_IMPORTED_MODULE_3__["default"], { handleClick: handleGoBack })),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_AddButton__WEBPACK_IMPORTED_MODULE_4__["default"], { handleClickButton: handleOpenCreateChartDialog }),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { display: 'flex', flexDirection: 'row' } }, iframeMap ? iframeMap.values() : null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_dialog_CreateChartDialog__WEBPACK_IMPORTED_MODULE_5__["default"], { open: createChartOpen, handleClose: (isCancel) => isCancel && setCreateChartOpen(false), sendNewMetrics: handleNewMetrics, sendNewUrl: (url) => handleSubmitUrl(url) })));
}


/***/ }),

/***/ "./lib/pages/DashboardChartView.js":
/*!*****************************************!*\
  !*** ./lib/pages/DashboardChartView.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ DashboardChartView)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _GeneralDashboard__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./GeneralDashboard */ "./lib/pages/GeneralDashboard.js");



function DashboardChartView({ 
// startDate,
// setStartDate,
// endDate,
// setEndDate,
children }) {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: {
                display: 'flex',
                flexDirection: 'row',
                justifyContent: 'space-between'
            } }),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { ..._GeneralDashboard__WEBPACK_IMPORTED_MODULE_2__.styles.chartsWrapper } }, children)));
}


/***/ }),

/***/ "./lib/pages/GeneralDashboard.js":
/*!***************************************!*\
  !*** ./lib/pages/GeneralDashboard.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ GeneralDashboard),
/* harmony export */   styles: () => (/* binding */ styles)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_ScaphChart__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../components/ScaphChart */ "./lib/components/ScaphChart.js");
/* harmony import */ var _components_MetricSelector__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../components/MetricSelector */ "./lib/components/MetricSelector.js");
/* harmony import */ var _helpers_constants__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../helpers/constants */ "./lib/helpers/constants.js");
/* harmony import */ var _components_TabPaper__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../components/TabPaper */ "./lib/components/TabPaper.js");
/* harmony import */ var _DashboardChartView__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./DashboardChartView */ "./lib/pages/DashboardChartView.js");







const styles = {
    main: {
        display: 'flex',
        flexDirection: 'row',
        width: '100%',
        height: '100%',
        flexWrap: 'wrap',
        boxSizing: 'border-box',
        padding: '10px',
        whiteSpace: 'nowrap'
    },
    grid: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
    },
    chartsWrapper: {
        display: 'flex',
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'center'
    },
    paper: {
        p: 2,
        width: '100%',
        borderRadius: 3,
        border: '1px solid #ccc',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center !important'
    }
};
function GeneralDashboard({ startDate, endDate, setStartDate, setEndDate, metrics, dataMap, selectedMetric, setSelectedMetric, loading }) {
    const Charts = [];
    for (let i = 0; i < _helpers_constants__WEBPACK_IMPORTED_MODULE_2__.NR_CHARTS; i++) {
        Charts.push(react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { mx: 5, my: 2 } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Paper, { elevation: 0, sx: styles.paper },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_MetricSelector__WEBPACK_IMPORTED_MODULE_3__["default"], { selectedMetric: selectedMetric[i], setSelectedMetric: newMetric => setSelectedMetric(i, newMetric), metrics: metrics }),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_ScaphChart__WEBPACK_IMPORTED_MODULE_4__["default"], { key: `${selectedMetric}-${i}`, rawData: dataMap.get(selectedMetric[i]) || [] }))));
    }
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { style: styles.main },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Paper, { key: "grid-element-main", style: {
                ...styles.grid,
                flexDirection: 'column',
                minWidth: '100%',
                minHeight: '300px',
                borderRadius: '15px',
                border: '1px solid #ccc'
            }, elevation: 0 }, loading ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CircularProgress, null)) : loading === false && metrics.length === 0 ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: {
                width: '100%',
                height: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                padding: '30px'
            } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "body2", sx: { textWrap: 'wrap' } }, "No metrics available/loaded. Write your username on the textfield above and click \"Refresh Metrics\" to see the metrics."))) : (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: { width: '100%', height: '100%' } },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_TabPaper__WEBPACK_IMPORTED_MODULE_5__["default"], null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_DashboardChartView__WEBPACK_IMPORTED_MODULE_6__["default"], { startDate: startDate, setStartDate: setStartDate, endDate: endDate, setEndDate: setEndDate }, Charts),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null, "Prediction page"),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null, "History")))))));
}


/***/ }),

/***/ "./lib/pages/GrafanaPage.js":
/*!**********************************!*\
  !*** ./lib/pages/GrafanaPage.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ GrafanaPage)
/* harmony export */ });
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_GoBackButton__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components/GoBackButton */ "./lib/components/GoBackButton.js");



const mc_grafana_url = 'https://mc-a4.lab.uvalight.net/grafana/';
function GrafanaPage({ handleGoBack }) {
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid2, { sx: { display: 'flex', flexDirection: 'column' } },
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid2, { sx: { display: 'flex' } },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_components_GoBackButton__WEBPACK_IMPORTED_MODULE_2__["default"], { handleClick: handleGoBack })),
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("iframe", { src: mc_grafana_url, width: "100%", height: "600", style: { border: 'none' } })));
}


/***/ }),

/***/ "./lib/pages/WelcomePage.js":
/*!**********************************!*\
  !*** ./lib/pages/WelcomePage.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (/* binding */ WelcomePage),
/* harmony export */   styles: () => (/* binding */ styles)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _GeneralDashboard__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./GeneralDashboard */ "./lib/pages/GeneralDashboard.js");
/* harmony import */ var _api_getScaphData__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../api/getScaphData */ "./lib/api/getScaphData.js");
/* harmony import */ var _helpers_constants__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../helpers/constants */ "./lib/helpers/constants.js");
/* harmony import */ var _components_FetchMetricsComponents__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../components/FetchMetricsComponents */ "./lib/components/FetchMetricsComponents.js");
/* harmony import */ var _components_KPIComponent__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../components/KPIComponent */ "./lib/components/KPIComponent.js");
/* harmony import */ var _api_apiScripts__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../api/apiScripts */ "./lib/api/apiScripts.js");
/* harmony import */ var _components_ApiSubmitForm__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ../components/ApiSubmitForm */ "./lib/components/ApiSubmitForm.js");
/* harmony import */ var _api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../api/handleNotebookContents */ "./lib/api/handleNotebookContents.js");
/* harmony import */ var _components_JupyterDialogWarning__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../components/JupyterDialogWarning */ "./lib/components/JupyterDialogWarning.js");











const styles = {
    main: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        width: '100%'
    },
    title: {
        fontWeight: 'bold',
        color: _helpers_constants__WEBPACK_IMPORTED_MODULE_2__.mainColour01,
        my: 2
    },
    topRibbon: {
        display: 'flex',
        width: '100%',
        gap: 3
    },
    buttonGrid: {
        display: 'flex',
        width: '100%',
        gap: 3,
        justifyContent: 'center',
        alignContent: 'center',
        '& .MuiButtonBase-root': {
            textTransform: 'none'
        },
        mb: 2
    }
};
function WelcomePage({ 
// handleRealTimeClick,
// handlePredictionClick,
// handleGrafanaClick,
username, panel }) {
    const [startDate, setStartDate] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(_helpers_constants__WEBPACK_IMPORTED_MODULE_2__.startDateJs);
    const [endDate, setEndDate] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(_helpers_constants__WEBPACK_IMPORTED_MODULE_2__.endDateJs);
    const [metrics, setMetrics] = react__WEBPACK_IMPORTED_MODULE_0___default().useState([]);
    const [dataMap, setDataMap] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(new Map());
    const [selectedMetric, setSelectedMetric] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(new Array(_helpers_constants__WEBPACK_IMPORTED_MODULE_2__.NR_CHARTS).fill(''));
    const [loading, setLoading] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    // const [isFetchMetrics, setIsFetchMetrics] = React.useState<boolean>(false);
    // const [fetchIntervalS, setFetchIntervalS] = React.useState<number>(30);
    const [openDialog, setOpenDialog] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    const [workflowList, setWorkflowList] = react__WEBPACK_IMPORTED_MODULE_0___default().useState([]);
    const [experimentList, setExperimentList] = react__WEBPACK_IMPORTED_MODULE_0___default().useState([]);
    const [selectedWorkflow, setSelectedWorkflow] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(null);
    const [selectedExperiment, setSelectedExperiment] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(null);
    function handleUpdateSelectedMetric(index, newMetric) {
        setSelectedMetric(prev => {
            const updated = [...prev];
            updated[index] = newMetric;
            return updated;
        });
    }
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        for (let i = 0; i < _helpers_constants__WEBPACK_IMPORTED_MODULE_2__.NR_CHARTS; i++) {
            if (selectedMetric[i] === '') {
                handleUpdateSelectedMetric(i, metrics[i] || '');
            }
        }
    }, [metrics]);
    async function fetchMetrics() {
        const container = document.getElementById(_helpers_constants__WEBPACK_IMPORTED_MODULE_2__.CONTAINER_ID);
        const scrollPosition = container === null || container === void 0 ? void 0 : container.scrollTop;
        setLoading(true);
        let startTimeUnix = 0;
        let endTimeUnix = 0;
        if (selectedWorkflow && selectedExperiment) {
            const timeStartEnd = await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_3__.handleGetTime)(selectedWorkflow, selectedExperiment, panel);
            if (timeStartEnd) {
                startTimeUnix = timeStartEnd.startTimeUnix;
                endTimeUnix = timeStartEnd.endTimeUnix;
            }
        }
        (0,_api_getScaphData__WEBPACK_IMPORTED_MODULE_4__["default"])({
            url: `https://mc-a4.lab.uvalight.net/prometheus-${username}`,
            startTime: startTimeUnix,
            endTime: endTimeUnix
        }).then(results => {
            if (container !== null && scrollPosition !== undefined) {
                container.scrollTop = scrollPosition;
            }
            if (results.size === 0) {
                console.error('No metrics found');
                setLoading(false);
                return;
            }
            setDataMap(results);
            const keys = Array.from(results.keys());
            setMetrics(keys);
            setLoading(false);
        });
    }
    function handleSetMetrics() {
        // setIsFetchMetrics(true);
        fetchMetrics();
    }
    async function handleSubmitValues(args) {
        if (selectedWorkflow && selectedExperiment) {
            const session_metrics = await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_3__.getHandleSessionMetrics)(selectedWorkflow, selectedExperiment, panel);
            const startEndTime = await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_3__.handleGetTime)(selectedWorkflow, selectedExperiment, panel);
            if (session_metrics && startEndTime) {
                const code = (0,_api_apiScripts__WEBPACK_IMPORTED_MODULE_5__.exportSendJson)({
                    ...args,
                    session_metrics,
                    creation_date: startEndTime.start_time,
                    experiment_id: selectedExperiment,
                    workflow_id: selectedWorkflow
                });
                console.log(code);
                (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_3__.handleNotebookSessionContents)(panel, code);
            }
            else {
                (0,_components_JupyterDialogWarning__WEBPACK_IMPORTED_MODULE_6__["default"])({
                    message: 'Could not get selected session metrics or creation date.'
                });
            }
        }
        else {
            (0,_components_JupyterDialogWarning__WEBPACK_IMPORTED_MODULE_6__["default"])({
                message: 'Could not get selected Experiment/Workflow.'
            });
        }
    }
    async function handleRefreshWorkflowList() {
        const newWorkflowList = await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_3__.handleLoadWorkflowList)(panel);
        setWorkflowList(newWorkflowList);
        setSelectedWorkflow(newWorkflowList[0]);
    }
    async function handleRefreshExperimentList() {
        if (selectedWorkflow) {
            const newExperimentList = await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_3__.handleLoadExperimentList)(selectedWorkflow, panel);
            setExperimentList(newExperimentList);
            setSelectedExperiment(newExperimentList[0]);
        }
    }
    async function handleInstallMetrics() {
        await (0,_api_handleNotebookContents__WEBPACK_IMPORTED_MODULE_3__.handleNotebookSessionContents)(panel, _api_apiScripts__WEBPACK_IMPORTED_MODULE_5__.installPrometheusScaphandre);
    }
    function handleSubmitExport() {
        setOpenDialog(true);
    }
    // React.useEffect(() => {
    //   let intervalId: NodeJS.Timeout;
    //   if (isFetchMetrics === true) {
    //     intervalId = setInterval(() => {
    //       fetchMetrics();
    //     }, fetchIntervalS * 1000);
    //   }
    //   return () => {
    //     if (intervalId) {
    //       return clearInterval(intervalId);
    //     }
    //   }; // Clear the interval Id when umounting ;)
    // }, [isFetchMetrics]);
    // Just run it once the component mounts.
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        handleRefreshWorkflowList();
    }, []);
    react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
        handleRefreshExperimentList();
    }, [workflowList, selectedWorkflow]);
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: styles.main },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "h4", sx: styles.title }, "\uD83C\uDF31\uD83C\uDF0D\u267B\uFE0F EcoJupyter Dashboard"),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: styles.topRibbon },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: {
                        width: '100%',
                        p: 2,
                        m: 2,
                        border: '1px solid #ccc',
                        borderRadius: '15px'
                    } },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_KPIComponent__WEBPACK_IMPORTED_MODULE_7__.KPIComponent, { rawMetrics: dataMap, experimentList: experimentList, workflowList: workflowList, handleSubmitExport: handleSubmitExport, handleRefreshExperimentList: handleRefreshWorkflowList, selectedExperiment: selectedExperiment, setSelectedExperiment: setSelectedExperiment, selectedWorkflow: selectedWorkflow, setSelectedWorkflow: setSelectedWorkflow }))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: styles.buttonGrid }),
            metrics && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid2, { sx: styles.topRibbon },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_FetchMetricsComponents__WEBPACK_IMPORTED_MODULE_8__["default"], { fetchMetrics: handleSetMetrics, 
                        // fetchInterval={fetchIntervalS}
                        // setFetchInterval={setFetchIntervalS}
                        // setIsFetchMetrics={setIsFetchMetrics}
                        handleInstallMetrics: handleInstallMetrics })),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_GeneralDashboard__WEBPACK_IMPORTED_MODULE_9__["default"], { startDate: startDate, setStartDate: setStartDate, setEndDate: setEndDate, endDate: endDate, metrics: metrics, dataMap: dataMap, selectedMetric: selectedMetric, setSelectedMetric: handleUpdateSelectedMetric, loading: loading })))),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_ApiSubmitForm__WEBPACK_IMPORTED_MODULE_10__["default"], { open: openDialog, setOpen: (newValue) => setOpenDialog(newValue), submitValues: handleSubmitValues })));
}


/***/ }),

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   MainWidget: () => (/* binding */ MainWidget),
/* harmony export */   Page: () => (/* binding */ Page)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _pages_ChartsPage__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./pages/ChartsPage */ "./lib/pages/ChartsPage.js");
/* harmony import */ var _pages_WelcomePage__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./pages/WelcomePage */ "./lib/pages/WelcomePage.js");
/* harmony import */ var _components_VerticalLinearStepper__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./components/VerticalLinearStepper */ "./lib/components/VerticalLinearStepper.js");
/* harmony import */ var _components_GoBackButton__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./components/GoBackButton */ "./lib/components/GoBackButton.js");
/* harmony import */ var _pages_GrafanaPage__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./pages/GrafanaPage */ "./lib/pages/GrafanaPage.js");
/* harmony import */ var _helpers_constants__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./helpers/constants */ "./lib/helpers/constants.js");









const styles = {
    main: {
        display: 'flex',
        flexDirection: 'row',
        width: '100%',
        height: '100%',
        flexWrap: 'wrap',
        boxSizing: 'border-box',
        padding: '3px'
    },
    grid: {
        display: 'flex',
        flexDirection: 'column',
        whiteSpace: 'wrap',
        // justifyContent: 'center',
        // alignItems: 'center',
        flex: '0 1 100%',
        width: '100%',
        height: '100%',
        overflow: 'auto',
        padding: '10px'
    }
};
function Prediction({ handleGoBack }) {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Grid2, { sx: { width: '100%', px: 3, py: 5 } },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_GoBackButton__WEBPACK_IMPORTED_MODULE_3__["default"], { handleClick: handleGoBack }),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_VerticalLinearStepper__WEBPACK_IMPORTED_MODULE_4__["default"], null)));
}
var Page;
(function (Page) {
    Page[Page["WelcomePage"] = 0] = "WelcomePage";
    Page[Page["ChartsPage"] = 1] = "ChartsPage";
    Page[Page["Prediction"] = 2] = "Prediction";
    Page[Page["Grafana"] = 3] = "Grafana";
})(Page || (Page = {}));
/**
 * React component for a counter.
 *
 * @returns The React component
 */
const App = ({ username, panel }) => {
    const [activePageState, setActivePageState] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(Page.WelcomePage);
    function handleRealTimeClick() {
        setActivePageState(Page.ChartsPage);
    }
    function handlePredictionClick() {
        setActivePageState(Page.Prediction);
    }
    function handleGrafanaClick() {
        setActivePageState(Page.Grafana);
    }
    function goToMainPage() {
        setActivePageState(Page.WelcomePage);
    }
    const ActivePage = {
        [Page.WelcomePage]: (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_pages_WelcomePage__WEBPACK_IMPORTED_MODULE_5__["default"], { handleRealTimeClick: handleRealTimeClick, handlePredictionClick: handlePredictionClick, handleGrafanaClick: handleGrafanaClick, username: username, panel: panel })),
        [Page.ChartsPage]: react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_pages_ChartsPage__WEBPACK_IMPORTED_MODULE_6__["default"], { handleGoBack: goToMainPage }),
        [Page.Prediction]: react__WEBPACK_IMPORTED_MODULE_0___default().createElement(Prediction, { handleGoBack: goToMainPage }),
        [Page.Grafana]: react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_pages_GrafanaPage__WEBPACK_IMPORTED_MODULE_7__["default"], { handleGoBack: goToMainPage })
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { style: styles.main },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Paper, { id: _helpers_constants__WEBPACK_IMPORTED_MODULE_8__.CONTAINER_ID, style: styles.grid }, ActivePage[activePageState])));
};
/**
 * A Counter Lumino Widget that wraps a CounterComponent.
 */
class MainWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ReactWidget {
    constructor(username, panel) {
        super();
        this.addClass('jp-ReactWidget');
        this._username = username;
        this._panel = panel;
    }
    render() {
        return react__WEBPACK_IMPORTED_MODULE_0___default().createElement(App, { username: this._username, panel: this._panel });
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.11f5590513d12505c034.js.map