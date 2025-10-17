"use client";

import { useState, useMemo } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  ColumnDef,
  SortingState,
  ColumnFiltersState,
} from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ChevronLeft, ChevronRight, Search, Download, ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";

interface ExcelTableProps {
  data: any[];
  columns?: ColumnDef<any>[];
  onExport?: () => void;
  showRowNumbers?: boolean;
  pageSize?: number;
}

export function ExcelTable({ 
  data, 
  columns: providedColumns, 
  onExport,
  showRowNumbers = true,
  pageSize = 50
}: ExcelTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState("");

  const columns = useMemo(() => {
    if (providedColumns) return providedColumns;
    
    if (data.length === 0) return [];
    
    const dataColumns = Object.keys(data[0]).map((key) => ({
      accessorKey: key,
      header: key,
      cell: ({ getValue }: any) => {
        const value = getValue();
        if (value === null || value === undefined) {
          return <span className="text-gray-400 italic">NULL</span>;
        }
        if (typeof value === "number") {
          return <span className="font-mono">{value.toLocaleString()}</span>;
        }
        return <span className="text-gray-900">{String(value)}</span>;
      },
    }));

    // Add row number column if enabled
    if (showRowNumbers) {
      return [
        {
          id: '_rowNumber',
          header: '#',
          cell: ({ row }: any) => (
            <span className="font-mono text-gray-500 text-xs">
              {row.index + 1}
            </span>
          ),
          size: 50,
        },
        ...dataColumns,
      ];
    }

    return dataColumns;
  }, [data, providedColumns, showRowNumbers]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    state: {
      sorting,
      columnFilters,
      globalFilter,
    },
    initialState: {
      pagination: {
        pageSize: pageSize,
      },
    },
  });

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-4 bg-white p-3 rounded-lg border border-gray-200">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="Search all columns..."
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="pl-9 bg-white border-gray-300"
          />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">
            {data.length} rows × {columns.length - (showRowNumbers ? 1 : 0)} columns
          </span>
          {onExport && (
            <Button variant="outline" size="sm" onClick={onExport} className="border-gray-300">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          )}
        </div>
      </div>

      {/* Excel-like Table */}
      <div className="rounded-lg border border-gray-300 shadow-sm overflow-hidden bg-white">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            {/* Header */}
            <thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id} className="bg-gradient-to-b from-gray-50 to-gray-100 border-b-2 border-gray-300">
                  {headerGroup.headers.map((header, index) => (
                    <th
                      key={header.id}
                      className={`
                        px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider
                        border-r border-gray-300 last:border-r-0
                        ${header.column.getCanSort() ? 'cursor-pointer hover:bg-gray-200 select-none' : ''}
                        ${index === 0 && showRowNumbers ? 'bg-gray-100 text-center w-16' : ''}
                      `}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      {header.isPlaceholder ? null : (
                        <div className="flex items-center gap-2 justify-between">
                          <span className="truncate">
                            {flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                          </span>
                          {header.column.getCanSort() && (
                            <span className="flex-shrink-0">
                              {header.column.getIsSorted() === 'asc' ? (
                                <ArrowUp className="h-3 w-3 text-blue-600" />
                              ) : header.column.getIsSorted() === 'desc' ? (
                                <ArrowDown className="h-3 w-3 text-blue-600" />
                              ) : (
                                <ArrowUpDown className="h-3 w-3 text-gray-400" />
                              )}
                            </span>
                          )}
                        </div>
                      )}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>

            {/* Body */}
            <tbody>
              {table.getRowModel().rows.length === 0 ? (
                <tr>
                  <td 
                    colSpan={columns.length} 
                    className="px-4 py-8 text-center text-gray-500 italic"
                  >
                    No data available
                  </td>
                </tr>
              ) : (
                table.getRowModel().rows.map((row, rowIndex) => (
                  <tr
                    key={row.id}
                    className={`
                      border-b border-gray-200 hover:bg-blue-50 transition-colors
                      ${rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                    `}
                  >
                    {row.getVisibleCells().map((cell, cellIndex) => (
                      <td
                        key={cell.id}
                        className={`
                          px-4 py-2.5 text-sm border-r border-gray-200 last:border-r-0
                          ${cellIndex === 0 && showRowNumbers ? 'bg-gray-50 text-center font-mono text-xs text-gray-500' : ''}
                        `}
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200">
        <div className="text-sm text-gray-600 font-medium">
          Showing{" "}
          <span className="font-bold text-gray-900">
            {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1}
          </span>
          {" "}to{" "}
          <span className="font-bold text-gray-900">
            {Math.min(
              (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
              data.length
            )}
          </span>
          {" "}of{" "}
          <span className="font-bold text-gray-900">{data.length}</span>
          {" "}rows
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
            className="border-gray-300"
          >
            First
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="border-gray-300"
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
          <span className="text-sm text-gray-600 px-2">
            Page{" "}
            <span className="font-bold text-gray-900">
              {table.getState().pagination.pageIndex + 1}
            </span>
            {" "}of{" "}
            <span className="font-bold text-gray-900">
              {table.getPageCount()}
            </span>
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="border-gray-300"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
            className="border-gray-300"
          >
            Last
          </Button>
        </div>
      </div>
    </div>
  );
}
