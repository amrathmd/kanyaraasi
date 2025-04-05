'use client';

import { useState, useEffect } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { UserCircleIcon } from '@heroicons/react/24/outline';
import { useRouter } from 'next/navigation';
import { Tab } from '@headlessui/react';

interface HeaderProps {
  userName?: string;
  balance?: number;
  role?: string;
  tabs?: {
    name: string;
    icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  }[];
  selectedTab?: number;
  onTabChange?: (index: number) => void;
  isBalanceLoading?: boolean;
}

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export default function Header({ 
  userName = 'User', 
  balance = 0, 
  role = 'USER',
  tabs,
  selectedTab = 0,
  onTabChange,
  isBalanceLoading = false
}: HeaderProps) {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    router.push('/login');
  };

  if (!mounted) return null;

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900 mr-8">
              {role === 'USER' ? 'User Dashboard' : 'Admin Dashboard'}
            </h1>
            
            {tabs && onTabChange && (
              <Tab.Group selectedIndex={selectedTab} onChange={onTabChange}>
                <Tab.List className="flex border-b border-gray-200">
                  {tabs.map((tab, index) => (
                    <Tab
                      key={tab.name}
                      className={({ selected }) =>
                        classNames(
                          'group flex-1 inline-flex items-center justify-center py-3 px-4 font-medium text-sm transition-all duration-200',
                          selected
                            ? 'text-indigo-600 border-b-2 border-indigo-500'
                            : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        )
                      }
                    >
                      <tab.icon
                        className={({ selected }) =>
                          classNames(
                            'mr-2 h-5 w-5 transition-colors duration-200',
                            selected ? 'text-indigo-500' : 'text-gray-400 group-hover:text-gray-500'
                          )
                        }
                        aria-hidden="true"
                      />
                      {tab.name}
                    </Tab>
                  ))}
                </Tab.List>
              </Tab.Group>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            {role === 'USER' && (
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Available Balance</p>
                {isBalanceLoading ? (
                  <div className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="text-lg font-semibold text-indigo-600">Loading...</span>
                  </div>
                ) : (
                  <p className="text-lg font-semibold text-indigo-600">₹{balance.toFixed(2)} INR</p>
                )}
              </div>
            )}
            
            <Menu as="div" className="relative">
              <Menu.Button className="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                <UserCircleIcon className="h-10 w-10 text-gray-400" />
              </Menu.Button>
              
              <Transition
                as={Fragment}
                enter="transition ease-out duration-100"
                enterFrom="transform opacity-0 scale-95"
                enterTo="transform opacity-100 scale-100"
                leave="transition ease-in duration-75"
                leaveFrom="transform opacity-100 scale-100"
                leaveTo="transform opacity-0 scale-95"
              >
                <Menu.Items className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none">
                  <div className="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
                    <p className="font-medium">{userName}</p>
                    <p className="text-xs text-gray-500">{role}</p>
                  </div>
                  <Menu.Item>
                    {({ active }) => (
                      <button
                        onClick={handleLogout}
                        className={classNames(
                          active ? 'bg-gray-100' : '',
                          'block w-full text-left px-4 py-2 text-sm text-gray-700'
                        )}
                      >
                        Sign out
                      </button>
                    )}
                  </Menu.Item>
                </Menu.Items>
              </Transition>
            </Menu>
          </div>
        </div>
      </div>
    </header>
  );
} 