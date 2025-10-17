"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Database, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { dataSourcesApi } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export function DataSourceConnector() {
  const [dbType, setDbType] = useState("postgresql");
  const [config, setConfig] = useState({
    name: "",
    host: "localhost",
    port: 5432,
    database: "",
    username: "",
    password: "",
    collection: "", // for MongoDB
  });
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState("");
  const [queryResult, setQueryResult] = useState<any>(null);
  const { toast } = useToast();

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    
    try {
      const response = await dataSourcesApi.testConnection({
        name: config.name,
        type: dbType,
        config: {
          host: config.host,
          port: config.port,
          database: config.database,
          username: config.username,
          password: config.password,
          ...(dbType === 'mongodb' && { collection: config.collection }),
        },
      });

      setTestResult(response.data);
      
      if (response.data.success) {
        toast({
          title: "Connection Successful",
          description: "Successfully connected to the database",
        });
        
        // Load tables
        await loadTables();
      }
    } catch (error: any) {
      setTestResult({ success: false, message: error.message });
      toast({
        title: "Connection Failed",
        description: error.response?.data?.detail || "Failed to connect to database",
        variant: "destructive",
      });
    } finally {
      setTesting(false);
    }
  };

  const loadTables = async () => {
    try {
      const response = await dataSourcesApi.listTables({
        name: config.name,
        type: dbType,
        config: {
          host: config.host,
          port: config.port,
          database: config.database,
          username: config.username,
          password: config.password,
        },
      });

      setTables(response.data.tables || []);
    } catch (error) {
      console.error("Failed to load tables:", error);
    }
  };

  const handleQueryTable = async () => {
    if (!selectedTable) return;

    try {
      const response = await dataSourcesApi.query(
        {
          name: config.name,
          type: dbType,
          config: {
            host: config.host,
            port: config.port,
            database: config.database,
            username: config.username,
            password: config.password,
          },
        },
        {
          query: dbType === 'mongodb' ? undefined : `SELECT * FROM ${selectedTable} LIMIT 100`,
          collection: dbType === 'mongodb' ? selectedTable : undefined,
          limit: 100,
        }
      );

      setQueryResult(response.data);
      toast({
        title: "Query Successful",
        description: `Fetched ${response.data.row_count} rows`,
      });
    } catch (error: any) {
      toast({
        title: "Query Failed",
        description: error.response?.data?.detail || "Failed to query database",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Database className="h-5 w-5" />
          <h3 className="text-lg font-semibold">Connect to Database</h3>
        </div>

        <Tabs value={dbType} onValueChange={setDbType}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="postgresql">PostgreSQL</TabsTrigger>
            <TabsTrigger value="mysql">MySQL</TabsTrigger>
            <TabsTrigger value="mongodb">MongoDB</TabsTrigger>
            <TabsTrigger value="sqlite">SQLite</TabsTrigger>
          </TabsList>

          <TabsContent value={dbType} className="space-y-4 mt-4">
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Connection Name</Label>
                <Input
                  id="name"
                  value={config.name}
                  onChange={(e) => setConfig({ ...config, name: e.target.value })}
                  placeholder="My Database"
                />
              </div>

              {dbType !== 'sqlite' && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="host">Host</Label>
                      <Input
                        id="host"
                        value={config.host}
                        onChange={(e) => setConfig({ ...config, host: e.target.value })}
                        placeholder="localhost"
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="port">Port</Label>
                      <Input
                        id="port"
                        type="number"
                        value={config.port}
                        onChange={(e) => setConfig({ ...config, port: parseInt(e.target.value) })}
                        placeholder={dbType === 'postgresql' ? '5432' : dbType === 'mysql' ? '3306' : '27017'}
                      />
                    </div>
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="database">Database</Label>
                    <Input
                      id="database"
                      value={config.database}
                      onChange={(e) => setConfig({ ...config, database: e.target.value })}
                      placeholder="mydb"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="username">Username</Label>
                      <Input
                        id="username"
                        value={config.username}
                        onChange={(e) => setConfig({ ...config, username: e.target.value })}
                        placeholder="user"
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="password">Password</Label>
                      <Input
                        id="password"
                        type="password"
                        value={config.password}
                        onChange={(e) => setConfig({ ...config, password: e.target.value })}
                        placeholder="••••••••"
                      />
                    </div>
                  </div>

                  {dbType === 'mongodb' && (
                    <div className="grid gap-2">
                      <Label htmlFor="collection">Collection (Optional)</Label>
                      <Input
                        id="collection"
                        value={config.collection}
                        onChange={(e) => setConfig({ ...config, collection: e.target.value })}
                        placeholder="mycollection"
                      />
                    </div>
                  )}
                </>
              )}

              {dbType === 'sqlite' && (
                <div className="grid gap-2">
                  <Label htmlFor="database_path">Database Path</Label>
                  <Input
                    id="database_path"
                    value={config.database}
                    onChange={(e) => setConfig({ ...config, database: e.target.value })}
                    placeholder="/path/to/database.db"
                  />
                </div>
              )}
            </div>

            <Button onClick={handleTestConnection} disabled={testing} className="w-full">
              {testing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Testing Connection...
                </>
              ) : (
                <>
                  <Database className="mr-2 h-4 w-4" />
                  Test Connection
                </>
              )}
            </Button>

            {testResult && (
              <div className={`flex items-center gap-2 p-3 rounded-lg ${
                testResult.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
              }`}>
                {testResult.success ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  <XCircle className="h-5 w-5" />
                )}
                <span className="text-sm font-medium">{testResult.message}</span>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </Card>

      {testResult?.success && tables.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Available Tables</h3>
          
          <div className="space-y-4">
            <Select value={selectedTable} onValueChange={setSelectedTable}>
              <SelectTrigger>
                <SelectValue placeholder="Select a table" />
              </SelectTrigger>
              <SelectContent>
                {tables.map((table) => (
                  <SelectItem key={table} value={table}>
                    {table}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button onClick={handleQueryTable} disabled={!selectedTable} className="w-full">
              Query Table
            </Button>
          </div>

          {queryResult && (
            <div className="mt-4">
              <p className="text-sm text-muted-foreground mb-2">
                Showing {queryResult.returned_rows} of {queryResult.row_count} rows
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      {queryResult.columns?.map((col: string) => (
                        <th key={col} className="text-left p-2 font-medium">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {queryResult.data?.slice(0, 10).map((row: any, i: number) => (
                      <tr key={i} className="border-b">
                        {queryResult.columns?.map((col: string) => (
                          <td key={col} className="p-2">
                            {String(row[col])}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
