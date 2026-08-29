/**
 * ===================================================================
 *  Google Apps Script backend for Field Location Tracker.
 *
 *  SHEET TABS REQUIRED:
 *    1. "Locations" - auto-created; log of every location sent.
 *    2. "WorkersDirectory" - YOU create this manually.
 *         Columns: WorkerID | Name | Phone
 *         Example row: FW-001 | Ali Raza | +923001234567
 *
 *  ENDPOINTS:
 *    POST /exec                -> log one location (used by worker app)
 *    GET  /exec?action=list    -> latest location per worker, with
 *                                  name/phone joined (used by supervisor map)
 * ===================================================================
 */

var API_KEY = "pakistan";
var LOCATIONS_SHEET = "Locations";
var DIRECTORY_SHEET = "WorkersDirectory";

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);

    if (API_KEY && data.api_key !== API_KEY) {
      return jsonResponse({ status: "error", message: "Unauthorized" }, 401);
    }
    if (!data.worker_id || data.latitude === undefined || data.longitude === undefined) {
      return jsonResponse({ status: "error", message: "Missing required fields" }, 400);
    }

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(LOCATIONS_SHEET);
    if (!sheet) {
      sheet = ss.insertSheet(LOCATIONS_SHEET);
      sheet.appendRow(["Server Timestamp", "Worker ID", "Latitude", "Longitude", "Accuracy (m)", "Captured At (device)"]);
    }

    sheet.appendRow([
      new Date(),
      data.worker_id,
      data.latitude,
      data.longitude,
      data.accuracy || "",
      data.captured_at || ""
    ]);

    return jsonResponse({ status: "success" }, 200);
  } catch (err) {
    return jsonResponse({ status: "error", message: err.toString() }, 500);
  }
}

function doGet(e) {
  var action = e.parameter.action;
  if (action === "list") {
    return jsonResponse(getLatestLocations(), 200);
  }
  if (action === "get_directory") {
    return getWorkersDirectory();
  }
  return jsonResponse({ status: "ok", message: "Field Location Tracker API is running" }, 200);
}

/**
 * Returns the list of authorized workers from WorkersDirectory sheet.
 * Used by worker app for login authentication.
 */
function getWorkersDirectory() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(DIRECTORY_SHEET);
  
  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify([]))
      .setMimeType(ContentService.MimeType.JSON);
  }
  
  var data = sheet.getDataRange().getValues();
  var workers = [];
  
  // Skip header row (row 0)
  for (var i = 1; i < data.length; i++) {
    if (data[i][0]) {  // If WorkerID exists
      workers.push({
        "WorkerID": String(data[i][0]).trim(),
        "Name": data[i][1] || "",
        "Phone": data[i][2] || ""
      });
    }
  }
  
  return ContentService.createTextOutput(JSON.stringify(workers))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * Returns one entry per worker: their most recent location, joined with
 * their name/phone from WorkersDirectory (falls back to worker_id as the
 * display name if the directory doesn't have them yet).
 */
function getLatestLocations() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var locSheet = ss.getSheetByName(LOCATIONS_SHEET);
  var dirSheet = ss.getSheetByName(DIRECTORY_SHEET);

  var directory = {};
  if (dirSheet) {
    var dirValues = dirSheet.getDataRange().getValues();
    for (var i = 1; i < dirValues.length; i++) {
      var row = dirValues[i];
      var workerId = String(row[0]).trim();
      if (!workerId) continue;
      directory[workerId] = { name: row[1] || workerId, phone: row[2] || "" };
    }
  }

  var latestByWorker = {};
  if (locSheet) {
    var values = locSheet.getDataRange().getValues();
    for (var j = 1; j < values.length; j++) {
      var r = values[j];
      var ts = r[0], wid = String(r[1]).trim(), lat = r[2], lon = r[3];
      if (!wid) continue;
      var existing = latestByWorker[wid];
      if (!existing || new Date(ts) > new Date(existing.timestamp)) {
        var dirEntry = directory[wid] || { name: wid, phone: "" };
        latestByWorker[wid] = {
          worker_id: wid,
          timestamp: ts,
          latitude: lat,
          longitude: lon,
          name: dirEntry.name,
          phone: dirEntry.phone
        };
      }
    }
  }

  return Object.keys(latestByWorker).map(function (k) {
    return latestByWorker[k];
  });
}

function jsonResponse(obj, code) {
  var output = ContentService.createTextOutput(JSON.stringify(obj));
  output.setMimeType(ContentService.MimeType.JSON);
  return output;
}
