import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  console.log('Request token:', token ? 'Token exists' : 'No token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // Remove Content-Type for FormData to let browser set it with boundary
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  return config;
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.response) {
      console.error('Response data:', JSON.stringify(error.response.data, null, 2));
      console.error('Response status:', error.response.status);
      console.error('Response headers:', error.response.headers);
      
      // If 401, check if we have a token
      if (error.response.status === 401) {
        const token = localStorage.getItem('token');
        console.error('Token in storage:', token ? 'EXISTS' : 'MISSING');
        console.error('Auth header sent:', error.config?.headers?.Authorization || 'NONE');
      }
    } else if (error.request) {
      console.error('No response received:', error.request);
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { username: email, password }),
  register: (email: string, password: string, fullName: string) =>
    api.post("/auth/register", { email, password, full_name: fullName }),
  me: () => api.get("/auth/me"),
};

export const filesApi = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    // Don't set Content-Type manually - let browser set it with boundary
    return api.post("/files/upload", formData);
  },
  list: () => api.get("/files/list"),
  get: (id: number) => api.get(`/files/${id}`),
  delete: (id: number) => api.delete(`/files/${id}`),
};

export const queryApi = {
  ask: (queryText: string, fileId?: number, sessionId?: string) =>
    api.post("/query/ask", { query_text: queryText, file_id: fileId, session_id: sessionId }),
  history: (limit: number = 20) => api.get(`/query/history?limit=${limit}`),
  get: (queryId: number) => api.get(`/query/${queryId}`),
};

export const dataApi = {
  profile: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/data/profile", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  clean: (file: File, operations: any) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("operations", JSON.stringify(operations));
    return api.post("/data/clean", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  recommendations: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/data/recommendations", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export const statisticsApi = {
  descriptive: (data: number[], columnName: string) =>
    api.post("/statistics/descriptive", { data, column_name: columnName }),
  compare: (groups: Record<string, number[]>, testType?: string) =>
    api.post("/statistics/compare", { groups, test_type: testType || "auto" }),
  correlation: (x: number[], y: number[], method?: string) =>
    api.post("/statistics/correlation", { x, y, method: method || "auto" }),
  regression: (x: any, y: number[], regressionType?: string) =>
    api.post("/statistics/regression", { x, y, regression_type: regressionType || "linear" }),
};

export const vizApi = {
  generate: (fileId: number, vizType: string, xColumn?: string, yColumn?: string, parameters?: any) =>
    api.post("/viz/generate", { file_id: fileId, viz_type: vizType, x_column: xColumn, y_column: yColumn, parameters }),
};

export const execApi = {
  execute: (code: string, fileId?: number, queryId?: number, timeoutSeconds?: number) =>
    api.post("/exec/execute", { code, file_id: fileId, query_id: queryId, timeout_seconds: timeoutSeconds || 30 }),
  validate: (code: string) =>
    api.post("/exec/validate", { code }),
};

export const notebooksApi = {
  create: (title?: string, cells?: any[]) =>
    api.post("/notebooks/", { title, cells }),
  list: () => api.get("/notebooks/"),
  get: (notebookId: string) => api.get(`/notebooks/${notebookId}`),
  update: (notebookId: string, title?: string, cells?: any[]) =>
    api.put(`/notebooks/${notebookId}`, { title, cells }),
  delete: (notebookId: string) => api.delete(`/notebooks/${notebookId}`),
  runCell: (notebookId: string, cellId: string) =>
    api.post(`/notebooks/${notebookId}/cells/${cellId}/run`),
  runAll: (notebookId: string) =>
    api.post(`/notebooks/${notebookId}/run_all`),
};

export const mlModelsApi = {
  list: (mine?: boolean) => api.get(`/ml_models/list${mine ? "?mine=true" : ""}`),
  train: (modelType: string, X: any, y: any, params?: any) =>
    api.post("/ml_models/train", { model_type: modelType, X, y, params }),
  predict: (modelId: string, X: any) =>
    api.post("/ml_models/predict", { model_id: modelId, X }),
  info: (modelId: string) => api.get(`/ml_models/info/${modelId}`),
  delete: (modelId: string) => api.delete(`/ml_models/${modelId}`),
};

export const transformationsApi = {
  renameColumn: (fileId: number, oldName: string, newName: string) =>
    api.post("/transform/columns/rename", { file_id: fileId, old_name: oldName, new_name: newName }),
  deleteColumn: (fileId: number, column: string) =>
    api.post("/transform/columns/delete", { file_id: fileId, column }),
  castColumn: (fileId: number, column: string, dataType: string) =>
    api.post("/transform/columns/cast", { file_id: fileId, column, data_type: dataType }),
  deriveColumn: (fileId: number, newColumn: string, formula: string) =>
    api.post("/transform/columns/derive", { file_id: fileId, new_column: newColumn, formula }),
  pivot: (fileId: number, index: string[], columns: string, values: string, aggfunc?: string) =>
    api.post("/transform/pivot", { file_id: fileId, index, columns, values, aggfunc }),
  filter: (fileId: number, filters: any[]) =>
    api.post("/transform/filter", { file_id: fileId, filters }),
  sort: (fileId: number, columns: string[], ascending: boolean[]) =>
    api.post("/transform/sort", { file_id: fileId, columns, ascending }),
  group: (fileId: number, groupBy: string[], aggregations: Record<string, string[]>) =>
    api.post("/transform/group", { file_id: fileId, group_by: groupBy, aggregations }),
};

export const sharingApi = {
  createShare: (analysisId: number, shareType: string, permissions: string[], expiresAt?: string) =>
    api.post("/sharing/share", { analysis_id: analysisId, share_type: shareType, permissions, expires_at: expiresAt }),
  getShared: (shareToken: string) =>
    api.get(`/sharing/shared/${shareToken}`),
  revokeShare: (shareToken: string) =>
    api.delete(`/sharing/share/${shareToken}`),
  addComment: (analysisId: number, content: string, parentId?: number) =>
    api.post("/sharing/comments", { analysis_id: analysisId, content, parent_id: parentId }),
  getComments: (analysisId: number) =>
    api.get(`/sharing/comments/${analysisId}`),
};

export const templatesApi = {
  list: (category?: string) =>
    api.get(`/templates${category ? `?category=${category}` : ""}`),
  get: (templateId: string) =>
    api.get(`/templates/${templateId}`),
  create: (name: string, description: string, category: string, config: any, isPublic?: boolean) =>
    api.post("/templates", { name, description, category, config, is_public: isPublic }),
  apply: (templateId: string, fileId: number) =>
    api.post(`/templates/${templateId}/apply`, { file_id: fileId }),
};

export const reportsApi = {
  createSchedule: (schedule: any) =>
    api.post("/reports/schedules", schedule),
  listSchedules: () =>
    api.get("/reports/schedules"),
  getSchedule: (scheduleId: number) =>
    api.get(`/reports/schedules/${scheduleId}`),
  updateSchedule: (scheduleId: number, schedule: any) =>
    api.put(`/reports/schedules/${scheduleId}`, schedule),
  deleteSchedule: (scheduleId: number) =>
    api.delete(`/reports/schedules/${scheduleId}`),
  runNow: (scheduleId: number) =>
    api.post(`/reports/schedules/${scheduleId}/run`),
};

export const aiApi = {
  chartSuggestions: (fileId: number) =>
    api.post(`/ai/chart-suggestions/${fileId}`),
  autoInsights: (fileId: number) =>
    api.post(`/ai/auto-insights/${fileId}`),
  detectTypes: (fileId: number) =>
    api.post(`/ai/detect-types/${fileId}`),
  sampleData: (fileId: number, sampleSize?: number, method?: string) =>
    api.post(`/ai/sample-data/${fileId}`, { sample_size: sampleSize, method }),
};

export const nlApi = {
  nlToChart: (fileId: number, query: string) =>
    api.post("/nl/nl-to-chart", { file_id: fileId, query }),
};

export const historyApi = {
  recordOperation: (fileId: number, operationType: string, parameters: any) =>
    api.post("/history/operations/record", { file_id: fileId, operation_type: operationType, parameters }),
  getHistory: (fileId: number) =>
    api.get(`/history/operations/history/${fileId}`),
  undo: (fileId: number) =>
    api.post(`/history/operations/undo/${fileId}`),
  redo: (fileId: number) =>
    api.post(`/history/operations/redo/${fileId}`),
  clearHistory: (fileId: number) =>
    api.post(`/history/operations/clear/${fileId}`),
};

export const versionsApi = {
  createVersion: (fileId: number, description?: string) =>
    api.post(`/versions/files/${fileId}/versions/create`, { description }),
  listVersions: (fileId: number) =>
    api.get(`/versions/files/${fileId}/versions`),
  restoreVersion: (fileId: number, versionName: string) =>
    api.post(`/versions/files/${fileId}/versions/restore`, { version_name: versionName }),
  compareVersions: (fileId: number, version1: string, version2: string) =>
    api.post(`/versions/files/${fileId}/versions/compare`, { version1_name: version1, version2_name: version2 }),
  deleteVersion: (fileId: number, versionName: string) =>
    api.delete(`/versions/files/${fileId}/versions/${versionName}`),
};

export const previewApi = {
  getFileData: (fileId: number, limit?: number, offset?: number) =>
    api.get(`/preview/files/${fileId}/data`, { params: { limit, offset } }),
  getColumns: (fileId: number) =>
    api.get(`/preview/files/${fileId}/columns`),
};

export const sqlApi = {
  execute: (fileId: number, query: string) =>
    api.post("/sql/execute", { file_id: fileId, query }),
  validate: (query: string) =>
    api.post("/sql/validate", { query }),
};

// Export API - Enhanced
export const exportApi = {
  exportPDF: (fileId: number) =>
    api.post(`/export/pdf/${fileId}`, {}, { responseType: 'blob' }),
  exportExcel: (fileId: number) =>
    api.post(`/export/excel/${fileId}`, {}, { responseType: 'blob' }),
  exportWord: (fileId: number) =>
    api.post(`/export/word/${fileId}`, {}, { responseType: 'blob' }),
  exportPowerPoint: (fileId: number) =>
    api.post(`/export/powerpoint/${fileId}`, {}, { responseType: 'blob' }),
  exportChartPNG: (chartConfig: any) =>
    api.post('/export/png/chart', chartConfig, { responseType: 'blob' }),
};

// Data Sources API
export const dataSourcesApi = {
  testConnection: (config: any) =>
    api.post('/datasources/test', config),
  connect: (config: any) =>
    api.post('/datasources/connect', config),
  listTables: (config: any) =>
    api.post('/datasources/tables', config),
  getSchema: (config: any, tableName: string) =>
    api.post('/datasources/schema', { ...config, table_name: tableName }),
  query: (config: any, queryRequest: any) =>
    api.post('/datasources/query', { ...config, ...queryRequest }),
};

// Enhanced Data Connectors API
export const connectorsApi = {
  listConnectors: () =>
    api.get('/connectors/connectors'),
  getConnectorInfo: (connectorType: string) =>
    api.get(`/connectors/connectors/${connectorType}`),
  testConnection: (datasource: any) =>
    api.post('/connectors/test', datasource),
  connect: (datasource: any) =>
    api.post('/connectors/connect', datasource),
  listTables: (datasource: any) =>
    api.post('/connectors/tables', datasource),
  query: (datasource: any, queryRequest: any) =>
    api.post('/connectors/query', { datasource, query_request: queryRequest }),
  preview: (datasource: any, tableName: string, limit?: number) =>
    api.post(`/connectors/preview?table_name=${tableName}&limit=${limit || 100}`, datasource),
  saveQuery: (datasource: any, queryRequest: any, filename: string) =>
    api.post('/connectors/query/save', { datasource, query_request: queryRequest, filename }),
};

// Advanced Charts API
export const advancedChartsApi = {
  generateHeatmap: (fileId: number, columns?: string[], method?: string) =>
    api.post('/charts/heatmap', { file_id: fileId, columns, method }),
  generateBoxPlot: (fileId: number, column: string, groupBy?: string) =>
    api.post('/charts/boxplot', { file_id: fileId, column, group_by: groupBy }),
  generateViolinPlot: (fileId: number, column: string, groupBy?: string, bins?: number) =>
    api.post('/charts/violin', { file_id: fileId, column, group_by: groupBy, bins }),
  generateHistogram: (fileId: number, column: string, bins?: number) =>
    api.post('/charts/histogram', { file_id: fileId, column, bins }),
  generateScatterMatrix: (fileId: number, columns?: string[], sampleSize?: number) =>
    api.post('/charts/scatter-matrix', { file_id: fileId, columns, sample_size: sampleSize }),
};

// Collaborative Editing API
export const collaborativeApi = {
  joinSession: (fileId: number, username: string) =>
    api.post('/collaborative/join', { file_id: fileId, username }),
  leaveSession: (fileId: number) =>
    api.post('/collaborative/leave', { file_id: fileId }),
  updateCursor: (fileId: number, position: any) =>
    api.post('/collaborative/cursor', { file_id: fileId, cursor_position: position }),
  broadcastChange: (fileId: number, change: any) =>
    api.post('/collaborative/broadcast', { file_id: fileId, change }),
  getSessionInfo: (fileId: number) =>
    api.get(`/collaborative/session/${fileId}`),
};

// Dashboard Builder API
export const dashboardsApi = {
  create: (name: string, description?: string, layout?: any) =>
    api.post('/dashboards', { name, description, layout }),
  list: (includePublic?: boolean) =>
    api.get(`/dashboards${includePublic ? '?include_public=true' : ''}`),
  get: (dashboardId: number) =>
    api.get(`/dashboards/${dashboardId}`),
  update: (dashboardId: number, updates: any) =>
    api.put(`/dashboards/${dashboardId}`, updates),
  delete: (dashboardId: number) =>
    api.delete(`/dashboards/${dashboardId}`),
  addWidget: (dashboardId: number, widget: any) =>
    api.post(`/dashboards/${dashboardId}/widgets`, widget),
  updateWidget: (dashboardId: number, widgetId: number, updates: any) =>
    api.put(`/dashboards/${dashboardId}/widgets/${widgetId}`, updates),
  removeWidget: (dashboardId: number, widgetId: number) =>
    api.delete(`/dashboards/${dashboardId}/widgets/${widgetId}`),
  duplicate: (dashboardId: number, newName?: string) =>
    api.post(`/dashboards/${dashboardId}/duplicate`, { new_name: newName }),
  export: (dashboardId: number) =>
    api.get(`/dashboards/${dashboardId}/export`),
  import: (dashboardData: any) =>
    api.post('/dashboards/import', dashboardData),
};
