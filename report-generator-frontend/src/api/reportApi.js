import { postJson, postBlob } from "./client";

export function generateAccomplishment(rawText) {
  return postJson("/api/generate-accomplishment", {
    raw_text: rawText,
  });
}

export function generateReportDocx(reportData) {
  return postBlob("/api/generate-docx", reportData);
}
