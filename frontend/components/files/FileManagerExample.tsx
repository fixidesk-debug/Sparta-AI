import React, { useState } from 'react';
import FileManager, { FileItem } from './FileManager';

// Sample data for demonstration
const sampleFiles: FileItem[] = [
  {
    id: '1',
    name: 'sales_data_2024.csv',
    type: 'csv' as const,
    size: 2048576,
    uploadDate: new Date(2024, 9, 10),
  },
  {
    id: '2',
    name: 'quarterly_report.xlsx',
    type: 'excel' as const,
    size: 5242880,
    uploadDate: new Date(2024, 9, 12),
  },
  {
    id: '3',
    name: 'config_settings.json',
    type: 'json' as const,
    size: 15360,
    uploadDate: new Date(2024, 9, 13),
  },
  {
    id: '4',
    name: 'company_logo.png',
    type: 'image' as const,
    size: 524288,
    uploadDate: new Date(2024, 9, 11),
    thumbnail: 'https://via.placeholder.com/240x180',
  },
  {
    id: '5',
    name: 'documentation.pdf',
    type: 'pdf' as const,
    size: 3145728,
    uploadDate: new Date(2024, 9, 9),
  },
  {
    id: '6',
    name: 'backup_archive.zip',
    type: 'archive' as const,
    size: 10485760,
    uploadDate: new Date(2024, 9, 8),
  },
  {
    id: '7',
    name: 'project_files',
    type: 'folder' as const,
    size: 0,
    uploadDate: new Date(2024, 9, 14),
  },
  {
    id: '8',
    name: 'analytics_dashboard.csv',
    type: 'csv' as const,
    size: 1572864,
    uploadDate: new Date(2024, 9, 13),
  },
];

const FileManagerExample: React.FC = () => {
  const [files, setFiles] = useState(sampleFiles);

  const handleUpload = (uploadedFiles: File[]) => {
    console.log('Uploading files:', uploadedFiles);
    
    // Simulate adding uploaded files to the list
    const newFiles: FileItem[] = uploadedFiles.map((file, index) => {
      const extension = file.name.split('.').pop()?.toLowerCase() || '';
      let fileType: FileItem['type'] = 'unknown';
      
      if (extension === 'csv') fileType = 'csv';
      else if (['xlsx', 'xls'].includes(extension)) fileType = 'excel';
      else if (extension === 'json') fileType = 'json';
      else if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(extension)) fileType = 'image';
      else if (extension === 'pdf') fileType = 'pdf';
      else if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension)) fileType = 'archive';
      
      return {
        id: `${Date.now()}-${index}`,
        name: file.name,
        type: fileType,
        size: file.size,
        uploadDate: new Date(),
      };
    });

    setFiles([...newFiles, ...files]);
  };

  const handleDelete = (fileIds: string[]) => {
    console.log('Deleting files:', fileIds);
    setFiles(files.filter(file => !fileIds.includes(file.id)));
  };

  const handleDownload = (fileIds: string[]) => {
    console.log('Downloading files:', fileIds);
    // Implement download logic here
  };

  return (
    <div style={{ width: '100%', height: '100vh', padding: '20px', background: '#f1f5f9' }}>
      <FileManager
        files={files}
        onUpload={handleUpload}
        onDelete={handleDelete}
        onDownload={handleDownload}
        maxFileSize={100 * 1024 * 1024} // 100MB
        allowedTypes={['*']}
      />
    </div>
  );
};

export default FileManagerExample;
