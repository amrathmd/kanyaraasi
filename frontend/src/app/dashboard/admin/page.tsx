'use client';

import { useState, useEffect } from 'react';
import { Document } from '@/types';
import { toast } from 'react-hot-toast';
import Header from '@/components/Header';
import { DocumentIcon, FunnelIcon, EyeIcon, CheckCircleIcon, XCircleIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import { getAdminDocuments, updateAdminDocumentStatus, getAdminApprovedDocuments } from '@/services/api';
import * as XLSX from 'xlsx';

export default function AdminDashboard() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [approvedDocuments, setApprovedDocuments] = useState<any[]>([]);
  const [selectedMonth, setSelectedMonth] = useState('all');
  const [userName, setUserName] = useState('Admin');
  const [balance, setBalance] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isApprovedLoading, setIsApprovedLoading] = useState(true);
  const [processingDocId, setProcessingDocId] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);

  useEffect(() => {
    // In a real app, you would fetch the admin's name and balance from an API
    const storedName = localStorage.getItem('userName') || 'Admin';
    setUserName(storedName);
    setBalance(5000); // Example balance
    
    // Fetch documents
    fetchDocuments();
  }, []);

  useEffect(() => {
    // Fetch approved documents when the Approved Documents tab is selected
    if (selectedTab === 1) {
      fetchApprovedDocuments();
    }
  }, [selectedTab]);

  const fetchDocuments = async () => {
    try {
      setIsLoading(true);
      const response = await getAdminDocuments();
      setDocuments(response.documents);
    } catch (error) {
      console.error('Error fetching documents:', error);
      toast.error('Failed to fetch documents');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchApprovedDocuments = async () => {
    try {
      setIsApprovedLoading(true);
      const response = await getAdminApprovedDocuments();
      setApprovedDocuments(response.documents);
    } catch (error) {
      console.error('Error fetching approved documents:', error);
      toast.error('Failed to fetch approved documents');
    } finally {
      setIsApprovedLoading(false);
    }
  };

  const handleStatusUpdate = async (documentId: string, status: 'APPROVED' | 'REJECTED') => {
    try {
      setProcessingDocId(documentId);
      await updateAdminDocumentStatus({ document_id: documentId, status });
      toast.success(`Document ${status.toLowerCase()} successfully`);
      // Refresh documents list
      await fetchDocuments();
    } catch (error) {
      console.error('Error updating document status:', error);
      toast.error(`Failed to ${status.toLowerCase()} document`);
    } finally {
      setProcessingDocId(null);
    }
  };

  const exportToExcel = () => {
    if (approvedDocuments.length === 0) {
      toast.error('No data to export');
      return;
    }

    try {
      // Format data for Excel
      const excelData = approvedDocuments.map(doc => ({
        'Document ID': doc.document_id,
        'Year': doc.year,
        'Month': doc.month,
        'Email': doc.email,
        'GST Number': doc.gst_number,
        'Total Amount (₹)': doc.total_amount,
        'CGST %': doc.cgst_percent,
        'SGST %': doc.sgst_percent
      }));

      // Create worksheet
      const ws = XLSX.utils.json_to_sheet(excelData);
      
      // Create workbook
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Approved Documents');
      
      // Generate Excel file
      const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
      const data = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      
      // Create download link
      const url = window.URL.createObjectURL(data);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `approved_documents_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.success('Excel file downloaded successfully');
    } catch (error) {
      console.error('Error exporting to Excel:', error);
      toast.error('Failed to export to Excel');
    }
  };

  const months = [
    { value: 'all', label: 'All Months' },
    { value: 'january', label: 'January' },
    { value: 'february', label: 'February' },
    { value: 'march', label: 'March' },
    { value: 'april', label: 'April' },
    { value: 'may', label: 'May' },
    { value: 'june', label: 'June' },
  ];

  const filteredDocuments = documents.filter((doc) => {
    if (selectedMonth === 'all') return true;
    return doc.month.toLowerCase() === selectedMonth;
  });

  const viewDocument = (url: string) => {
    window.open(url, '_blank');
  };

  const tabs = [
    { name: 'All Documents', icon: DocumentIcon },
    { name: 'Approved Documents', icon: CheckCircleIcon },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        userName={userName} 
        balance={balance} 
        role="ADMIN" 
        tabs={tabs}
        selectedTab={selectedTab}
        onTabChange={setSelectedTab}
      />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
            <div>
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                {selectedTab === 0 ? 'Document Management' : 'Approved Documents'}
              </h3>
              <p className="mt-1 max-w-2xl text-sm text-gray-500">
                {selectedTab === 0 
                  ? 'Manage and review all uploaded documents.' 
                  : 'View all approved documents with their details.'}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              {selectedTab === 0 ? (
                <div className="flex items-center">
                  <FunnelIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <select
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    {months.map((month) => (
                      <option key={month.value} value={month.value}>
                        {month.label}
                      </option>
                    ))}
                  </select>
                </div>
              ) : (
                <button
                  onClick={exportToExcel}
                  disabled={approvedDocuments.length === 0 || isApprovedLoading}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                  Export to Excel
                </button>
              )}
            </div>
          </div>
          <div className="border-t border-gray-200">
            <div className="overflow-x-auto">
              {selectedTab === 0 ? (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Document ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Year
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Month
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {isLoading ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-4 text-center">
                          <div className="flex justify-center items-center">
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Loading documents...
                          </div>
                        </td>
                      </tr>
                    ) : filteredDocuments.length > 0 ? (
                      filteredDocuments.map((doc) => (
                        <tr key={doc.document_id} className="hover:bg-gray-50 transition-colors duration-150">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <DocumentIcon className="h-5 w-5 text-gray-400 mr-2" />
                              <span className="text-sm font-medium text-gray-900">
                                {doc.document_id}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {doc.year}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {doc.month}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              doc.status === 'UPLOADED' 
                                ? 'bg-blue-100 text-blue-800' 
                                : doc.status === 'APPROVED'
                                ? 'bg-green-100 text-green-800'
                                : doc.status === 'REJECTED'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {doc.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                            <button
                              onClick={() => viewDocument(doc.url)}
                              className="text-indigo-600 hover:text-indigo-900 inline-flex items-center"
                            >
                              <EyeIcon className="h-5 w-5 mr-1" />
                              View
                            </button>
                            {doc.status === 'UPLOADED' && (
                              <>
                                <button
                                  onClick={() => handleStatusUpdate(doc.document_id, 'APPROVED')}
                                  disabled={processingDocId === doc.document_id}
                                  className="text-green-600 hover:text-green-900 inline-flex items-center ml-2"
                                >
                                  <CheckCircleIcon className="h-5 w-5 mr-1" />
                                  {processingDocId === doc.document_id ? 'Processing...' : 'Approve'}
                                </button>
                                <button
                                  onClick={() => handleStatusUpdate(doc.document_id, 'REJECTED')}
                                  disabled={processingDocId === doc.document_id}
                                  className="text-red-600 hover:text-red-900 inline-flex items-center ml-2"
                                >
                                  <XCircleIcon className="h-5 w-5 mr-1" />
                                  {processingDocId === doc.document_id ? 'Processing...' : 'Reject'}
                                </button>
                              </>
                            )}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">
                          No documents found for the selected month.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              ) : (
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Document ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Year
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Month
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        GST Number
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        CGST %
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        SGST %
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {isApprovedLoading ? (
                      <tr>
                        <td colSpan={8} className="px-6 py-4 text-center">
                          <div className="flex justify-center items-center">
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Loading approved documents...
                          </div>
                        </td>
                      </tr>
                    ) : approvedDocuments.length > 0 ? (
                      approvedDocuments.map((doc) => (
                        <tr key={doc.document_id} className="hover:bg-gray-50 transition-colors duration-150">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <DocumentIcon className="h-5 w-5 text-gray-400 mr-2" />
                              <span className="text-sm font-medium text-gray-900">
                                {doc.document_id}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {doc.year}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {doc.month}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {doc.email}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {doc.gst_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ₹{doc.total_amount.toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {doc.cgst_percent}%
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {doc.sgst_percent}%
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={8} className="px-6 py-4 text-center text-sm text-gray-500">
                          No approved documents found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 