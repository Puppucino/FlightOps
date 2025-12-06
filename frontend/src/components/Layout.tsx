import React from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import './Layout.css'

interface LayoutProps {
  children: React.ReactNode
  searchQuery?: string
  onSearchChange?: (value: string) => void
  title?: string
  showBackButton?: boolean
}

export const Layout: React.FC<LayoutProps> = ({ 
  children, 
  searchQuery, 
  onSearchChange, 
  title, 
  showBackButton 
}) => {
  return (
    <div className="App">
      <Sidebar />
      <div className="main-content">
        <Header 
          searchQuery={searchQuery}
          onSearchChange={onSearchChange}
          title={title}
          showBackButton={showBackButton}
        />
        <main className="main-body">
          {children}
        </main>
      </div>
    </div>
  )
}
