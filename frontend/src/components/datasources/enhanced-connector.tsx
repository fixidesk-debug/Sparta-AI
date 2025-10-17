"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Database, CheckCircle, XCircle, Loader2, Table, 
  Search, Download, Play, Cloud, Server 
} from "lucide-react";
import { connectorsApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { ExcelTable } from "@/components/data/excel-table";

interface ConnectorInfo {
  type: string;
  name: string;
  type_category: string;
  required_fields: string[];
  optional_fields: string[];
  default_port?: number;
}

export function EnhancedConnector() {
  const [connectors, setConnectors] = useState<ConnectorInfo[]>([]);
  const [selectedConnector, setSelectedConnector] = useState<string>("");
  const [connectorInfo, setConnectorInfo] = useState<ConnectorInfo | null>(null);
  const [config, setConfig] = useState<Record<string, any>>({});
  const [connectionName, setConnectionName] = useState("");
  const [testing, setTesting] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState("");
  const [customQuery, setCustomQuery] = useState("");
  const [queryMode, setQueryMode] = useState<"table" | "custom">("table");
  const [queryResult, setQueryResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadConnectors();
  }, []);

  useEffect(() => {
    if (selectedConnector) {
      loadConnectorInfo(selectedConnector);
      // Reset config when connector changes
      setConfig({});
      setTestResult(null);
      setTables([]);
    }
  }, [selectedConnector]);

  const loadConnectors = async () => {
    try {
      const response = await connectorsApi.listConnectors();
      setConnectors(response.data.connectors || []);
      if (response.data.connectors.length > 0) {
        setSelectedConnector(response.data.connectors[0].type);
      }
    } catch (error) {
      console.error("Failed to load connectors:", error);
      toast({
        title: "Error",
        description: "Failed to load available connectors",
        variant: "destructive",
      });
    }
  };

  const loadConnectorInfo = async (connectorType: string) => {
    try {
      const response = await connectorsApi.getConnectorInfo(connectorType);
      setConnectorInfo(response.data);
      
      // Initialize config with default values
      const initialConfig: Record<string, any> = {};
      if (response.data.default_port) {
        initialConfig.port = response.data.default_port;
      }
      setConfig(initialConfig);
    } catch (error) {
      console.error("Failed to load connector info:", error);
    }
  };

  const handleTestConnection = async () => {
    if (!connectionName.trim()) {
      toast({
        title: "Connection Name Required",
        description: "Please provide a name for this connection",
        variant: "destructive",
      });
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const response = await connectorsApi.testConnection({
        name: connectionName,
        type: selectedConnector,
        config: config,
      });

      setTestResult(response.data);

      if (response.data.success) {
        toast({
          title: "Connection Successful! ✅",
          description: response.data.message,
        });
        // Load tables after successful connection
        await loadTables();
      } else {
        toast({
          title: "Connection Failed",
          description: response.data.message,
          variant: "destructive",
        });
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message;
      setTestResult({ success: false, message: errorMsg });
      toast({
        title: "Connection Failed",
        description: errorMsg,
        variant: "destructive",
      });
    } finally {
      setTesting(false);
    }
  };

  const handleConnect = async () => {
    setConnecting(true);
    try {
      const response = await connectorsApi.connect({
        name: connectionName,
        type: selectedConnector,
        config: config,
      });

      toast({
        title: "Connected Successfully!",
        description: `Connected to ${response.data.name}`,
      });
    } catch (error: any) {
      toast({
        title: "Connection Failed",
        description: error.response?.data?.detail || "Failed to establish connection",
        variant: "destructive",
      });
    } finally {
      setConnecting(false);
    }
  };

  const loadTables = async () => {
    try {
      const response = await connectorsApi.listTables({
        name: connectionName,
        type: selectedConnector,
        config: config,
      });

      setTables(response.data.tables || []);
      toast({
        title: "Tables Loaded",
        description: `Found ${response.data.tables?.length || 0} tables/collections`,
      });
    } catch (error: any) {
      console.error("Failed to load tables:", error);
      toast({
        title: "Failed to Load Tables",
        description: error.response?.data?.detail || "Could not retrieve table list",
        variant: "destructive",
      });
    }
  };

  const handlePreviewTable = async () => {
    if (!selectedTable) return;

    setLoading(true);
    try {
      const response = await connectorsApi.preview(
        {
          name: connectionName,
          type: selectedConnector,
          config: config,
        },
        selectedTable,
        100
      );

      setQueryResult(response.data);
      toast({
        title: "Preview Loaded",
        description: `Showing ${response.data.returned_rows} rows from ${selectedTable}`,
      });
    } catch (error: any) {
      toast({
        title: "Preview Failed",
        description: error.response?.data?.detail || "Failed to preview table",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCustomQuery = async () => {
    if (!customQuery.trim()) {
      toast({
        title: "Query Required",
        description: "Please enter a query",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const response = await connectorsApi.query(
        {
          name: connectionName,
          type: selectedConnector,
          config: config,
        },
        {
          query: customQuery,
          limit: 1000,
        }
      );

      setQueryResult(response.data);
      toast({
        title: "Query Executed",
        description: `Retrieved ${response.data.returned_rows} rows`,
      });
    } catch (error: any) {
      toast({
        title: "Query Failed",
        description: error.response?.data?.detail || "Failed to execute query",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveResults = async () => {
    if (!queryResult) return;

    const filename = `${connectionName}_${selectedTable || 'query'}_${Date.now()}.csv`;
    
    try {
      await connectorsApi.saveQuery(
        {
          name: connectionName,
          type: selectedConnector,
          config: config,
        },
        {
          query: customQuery || `SELECT * FROM ${selectedTable}`,
          limit: 10000,
        },
        filename
      );

      toast({
        title: "Results Saved",
        description: `Data saved as ${filename}`,
      });
    } catch (error: any) {
      toast({
        title: "Save Failed",
        description: error.response?.data?.detail || "Failed to save results",
        variant: "destructive",
      });
    }
  };

  const renderConfigField = (field: string) => {
    const isPassword = field.toLowerCase().includes('password') || field.toLowerCase().includes('token');
    const isTextarea = field.toLowerCase().includes('json') || field.toLowerCase().includes('credentials');
    const isNumber = field.toLowerCase().includes('port');

    return (
      <div key={field} className="grid gap-2">
        <Label htmlFor={field} className="capitalize">
          {field.replace(/_/g, ' ')}
          {connectorInfo?.required_fields.includes(field) && (
            <span className="text-red-500 ml-1">*</span>
          )}
        </Label>
        {isTextarea ? (
          <Textarea
            id={field}
            value={config[field] || ''}
            onChange={(e) => setConfig({ ...config, [field]: e.target.value })}
            placeholder={`Enter ${field.replace(/_/g, ' ')}`}
            rows={3}
          />
        ) : (
          <Input
            id={field}
            type={isPassword ? 'password' : isNumber ? 'number' : 'text'}
            value={config[field] || ''}
            onChange={(e) => setConfig({ 
              ...config, 
              [field]: isNumber ? parseInt(e.target.value) || '' : e.target.value 
            })}
            placeholder={`Enter ${field.replace(/_/g, ' ')}`}
          />
        )}
      </div>
    );
  };

  const getConnectorIcon = (type: string) => {
    if (type.includes('cloud') || ['bigquery', 'snowflake', 'databricks'].includes(type)) {
      return <Cloud className="h-5 w-5" />;
    }
    return <Server className="h-5 w-5" />;
  };

  return (
    <div className="space-y-6">
      {/* Connector Selection */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Database className="h-6 w-6 text-primary" />
          <h2 className="text-2xl font-bold">Connect to External Data Source</h2>
        </div>
        <p className="text-muted-foreground mb-6">
          Connect to databases, cloud warehouses, and other data sources to analyze your data
        </p>

        {/* Connector Type Selection */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
          {connectors.map((connector) => (
            <button
              key={connector.type}
              onClick={() => setSelectedConnector(connector.type)}
              className={`p-4 rounded-lg border-2 transition-all ${
                selectedConnector === connector.type
                  ? 'border-primary bg-primary/10'
                  : 'border-gray-200 hover:border-primary/50'
              }`}
            >
              <div className="flex flex-col items-center gap-2">
                {getConnectorIcon(connector.type)}
                <span className="text-sm font-medium text-center">{connector.name}</span>
                <span className="text-xs text-muted-foreground">{connector.type_category}</span>
              </div>
            </button>
          ))}
        </div>

        {/* Connection Configuration */}
        {connectorInfo && (
          <div className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="connection_name">
                Connection Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="connection_name"
                value={connectionName}
                onChange={(e) => setConnectionName(e.target.value)}
                placeholder="My Production Database"
              />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {connectorInfo.required_fields.map(renderConfigField)}
              {connectorInfo.optional_fields.map(renderConfigField)}
            </div>

            <div className="flex gap-3">
              <Button 
                onClick={handleTestConnection} 
                disabled={testing || !connectionName.trim()}
                className="flex-1"
              >
                {testing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Test Connection
                  </>
                )}
              </Button>

              {testResult?.success && (
                <Button 
                  onClick={handleConnect} 
                  disabled={connecting}
                  variant="default"
                  className="flex-1"
                >
                  {connecting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <Database className="mr-2 h-4 w-4" />
                      Connect
                    </>
                  )}
                </Button>
              )}
            </div>

            {testResult && (
              <div
                className={`flex items-center gap-2 p-4 rounded-lg ${
                  testResult.success
                    ? 'bg-green-50 text-green-700 border border-green-200'
                    : 'bg-red-50 text-red-700 border border-red-200'
                }`}
              >
                {testResult.success ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  <XCircle className="h-5 w-5" />
                )}
                <div className="flex-1">
                  <p className="font-medium">{testResult.success ? 'Success!' : 'Failed'}</p>
                  <p className="text-sm">{testResult.message}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Tables and Query Interface */}
      {testResult?.success && tables.length > 0 && (
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Table className="h-5 w-5 text-primary" />
            <h3 className="text-xl font-semibold">Query Data</h3>
          </div>

          <Tabs value={queryMode} onValueChange={(v) => setQueryMode(v as any)}>
            <TabsList className="grid w-full grid-cols-2 mb-4">
              <TabsTrigger value="table">Browse Tables</TabsTrigger>
              <TabsTrigger value="custom">Custom Query</TabsTrigger>
            </TabsList>

            <TabsContent value="table" className="space-y-4">
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="table-select">Select Table ({tables.length} available)</Label>
                  <select
                    id="table-select"
                    value={selectedTable}
                    onChange={(e) => setSelectedTable(e.target.value)}
                    className="w-full p-2 border rounded-md"
                    aria-label="Select database table"
                  >
                    <option value="">Choose a table...</option>
                    {tables.map((table) => (
                      <option key={table} value={table}>
                        {table}
                      </option>
                    ))}
                  </select>
                </div>

                <Button
                  onClick={handlePreviewTable}
                  disabled={!selectedTable || loading}
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Loading Preview...
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-4 w-4" />
                      Preview Table (100 rows)
                    </>
                  )}
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="custom" className="space-y-4">
              <div className="grid gap-2">
                <Label htmlFor="custom_query">SQL Query</Label>
                <Textarea
                  id="custom_query"
                  value={customQuery}
                  onChange={(e) => setCustomQuery(e.target.value)}
                  placeholder="SELECT * FROM users WHERE created_at > '2024-01-01' LIMIT 1000"
                  rows={6}
                  className="font-mono text-sm"
                />
              </div>

              <Button
                onClick={handleCustomQuery}
                disabled={!customQuery.trim() || loading}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Executing Query...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    Execute Query
                  </>
                )}
              </Button>
            </TabsContent>
          </Tabs>

          {/* Query Results - Excel-like Table */}
          {queryResult && queryResult.data && queryResult.data.length > 0 && (
            <div className="mt-6">
              <ExcelTable 
                data={queryResult.data}
                onExport={handleSaveResults}
                showRowNumbers={true}
                pageSize={50}
              />
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
