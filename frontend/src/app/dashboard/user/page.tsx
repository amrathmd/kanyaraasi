'use client';

import { useState, useEffect, useRef } from 'react';
import { Document } from '@/types';
import { toast } from 'react-hot-toast';
import Header from '@/components/Header';
import { DocumentIcon, ArrowUpTrayIcon, XMarkIcon, CheckCircleIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

export default function UserDashboard() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectedTab, setSelectedTab] = useState(0);
  const [userName, setUserName] = useState('User');
  const [balance, setBalance] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // In a real app, you would fetch the user's name and balance from an API
    const storedName = localStorage.getItem('userName') || 'User';
    setUserName(storedName);
    setBalance(1000); // Example balance
  }, []);

  const tabs = [
    { name: 'Upload Document', icon: ArrowUpTrayIcon },
    { name: 'My Documents', icon: DocumentIcon },
  ];

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      setSelectedFiles(prev => [...prev, ...files]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      setSelectedFiles(prev => [...prev, ...files]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Please select at least one file');
      return;
    }

    try {
      // Create a FormData object for each file
      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append('file', file);
        
        // TODO: Implement file upload API call
        // await uploadFile(formData);
      }
      
      toast.success(`${selectedFiles.length} file(s) uploaded successfully`);
      setSelectedFiles([]);
    } catch (error) {
      toast.error('Failed to upload files');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <Header 
        userName={userName} 
        balance={balance} 
        role="USER" 
        tabs={tabs}
        selectedTab={selectedTab}
        onTabChange={setSelectedTab}
      />
      
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="mt-6">
          {selectedTab === 0 ? (
            <div className="bg-white shadow-xl rounded-xl p-8 border border-gray-100">
              <div className="space-y-6">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">Upload documents</h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Select one or more files to upload to your account.
                  </p>
                </div>
                
                <div 
                  className={`mt-6 transition-all duration-200 ${
                    isDragging 
                      ? 'bg-indigo-50 border-indigo-300 shadow-md' 
                      : 'bg-white border-gray-200'
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  <div className="mt-1 flex justify-center px-6 pt-8 pb-8 border-2 border-dashed rounded-xl">
                    <div className="space-y-3 text-center">
                      <div className={`mx-auto h-16 w-16 rounded-full flex items-center justify-center ${
                        isDragging ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-400'
                      }`}>
                        <ArrowUpTrayIcon className="h-8 w-8" />
                      </div>
                      <div className="flex text-sm text-gray-600 justify-center">
                        <label
                          htmlFor="file-upload"
                          className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
                        >
                          <span>Upload files</span>
                          <input
                            id="file-upload"
                            name="file-upload"
                            type="file"
                            multiple
                            className="sr-only"
                            onChange={handleFileUpload}
                            ref={fileInputRef}
                          />
                        </label>
                        <p className="pl-1">or drag and drop</p>
                      </div>
                      <p className="text-xs text-gray-500">PDF, DOC, DOCX up to 10MB each</p>
                    </div>
                  </div>
                </div>
                
                {selectedFiles.length > 0 && (
                  <div className="mt-6">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Selected files ({selectedFiles.length})</h4>
                    <ul className="divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden">
                      {selectedFiles.map((file, index) => (
                        <li key={index} className="pl-4 pr-4 py-3 flex items-center justify-between text-sm bg-white hover:bg-gray-50 transition-colors duration-150">
                          <div className="w-0 flex-1 flex items-center">
                            <div className="flex-shrink-0 h-10 w-10 rounded-md bg-indigo-50 flex items-center justify-center">
                              <DocumentTextIcon className="h-6 w-6 text-indigo-500" />
                            </div>
                            <div className="ml-3 flex-1">
                              <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                              <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                            </div>
                          </div>
                          <div className="ml-4 flex-shrink-0">
                            <button
                              type="button"
                              onClick={() => removeFile(index)}
                              className="font-medium text-red-600 hover:text-red-500 focus:outline-none focus:underline"
                            >
                              <XMarkIcon className="h-5 w-5" />
                            </button>
                          </div>
                        </li>
                      ))}
                    </ul>
                    
                    <div className="mt-6 flex justify-end">
                      <button
                        onClick={() => setSelectedFiles([])}
                        className="mr-3 inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      >
                        Clear all
                      </button>
                      <button
                        onClick={handleUpload}
                        className="inline-flex items-center px-5 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200"
                      >
                        Upload {selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white shadow-xl rounded-xl overflow-hidden border border-gray-100">
              <div className="px-6 py-5 sm:px-8">
                <h3 className="text-2xl font-bold text-gray-900">My Documents</h3>
                <p className="mt-2 max-w-2xl text-sm text-gray-500">
                  A list of all your uploaded documents.
                </p>
              </div>
              <div className="border-t border-gray-200">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Document Name
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Upload Date
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-4 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {documents.length > 0 ? (
                        documents.map((doc) => (
                          <tr key={doc.id} className="hover:bg-gray-50 transition-colors duration-150">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                <div className="flex-shrink-0 h-10 w-10 rounded-md bg-indigo-50 flex items-center justify-center">
                                  <DocumentTextIcon className="h-6 w-6 text-indigo-500" />
                                </div>
                                <div className="ml-3">
                                  <p className="text-sm font-medium text-gray-900">{doc.name}</p>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {new Date(doc.uploadedAt).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                Active
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                              <button className="text-indigo-600 hover:text-indigo-900 mr-4 transition-colors duration-200">
                                Download
                              </button>
                              <button className="text-red-600 hover:text-red-900 transition-colors duration-200">
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="px-6 py-12 text-center">
                            <div className="mx-auto h-16 w-16 rounded-full bg-gray-100 flex items-center justify-center mb-4">
                              <DocumentIcon className="h-8 w-8 text-gray-400" />
                            </div>
                            <p className="text-sm text-gray-500 mb-4">No documents found. Upload your first document to get started.</p>
                            <button 
                              onClick={() => setSelectedTab(0)}
                              className="inline-flex items-center px-5 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200"
                            >
                              Upload Document
                            </button>
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
} 