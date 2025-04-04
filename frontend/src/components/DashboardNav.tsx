'use client';

import { Tab } from '@headlessui/react';
import { DocumentIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline';

interface DashboardNavProps {
  tabs: {
    name: string;
    icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  }[];
  selectedIndex: number;
  onChange: (index: number) => void;
}

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export default function DashboardNav({ tabs, selectedIndex, onChange }: DashboardNavProps) {
  return (
    <div className="border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <Tab.Group selectedIndex={selectedIndex} onChange={onChange}>
          <Tab.List className="flex space-x-8 py-4">
            {tabs.map((tab) => (
              <Tab
                key={tab.name}
                className={({ selected }) =>
                  classNames(
                    'group inline-flex items-center py-2 px-1 border-b-2 font-medium text-sm',
                    selected
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  )
                }
              >
                <tab.icon
                  className={({ selected }) =>
                    classNames(
                      'mr-2 h-5 w-5',
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
      </div>
    </div>
  );
} 