import { getJson, postFile, deleteRequest } from "./client";

export function getKnowledgeDocuments() {
  return getJson("/api/knowledge");
}

export function getKnowledgeDocument(reportId) {
  return getJson(`/api/knowledge/${reportId}`);
}

export function uploadKnowledgeDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  return postFile("/api/knowledge/upload", formData);
}

export function deleteKnowledgeDocument(reportId) {
  return deleteRequest(`/api/knowledge/${reportId}`);
}
