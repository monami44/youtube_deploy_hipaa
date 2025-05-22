"use client"

import Link from "next/link"
import { FileText, PlusCircle, Home } from "lucide-react"

export function Sidebar() {
  return (
    <aside className="w-64 bg-muted h-screen p-4 hidden md:block">
      <div className="mb-8">
        <h2 className="text-xl font-bold">Document Processor</h2>
        <p className="text-sm text-muted-foreground">HIPAA Compliant</p>
      </div>
      
      <nav className="space-y-2">
        <Link href="/" className="flex items-center p-2 rounded-md hover:bg-accent">
          <Home className="mr-2 h-4 w-4" />
          <span>Dashboard</span>
        </Link>
        <Link href="/upload" className="flex items-center p-2 rounded-md hover:bg-accent">
          <PlusCircle className="mr-2 h-4 w-4" />
          <span>Upload Document</span>
        </Link>
        <div className="pt-4 border-t mt-4">
          <p className="text-xs font-medium text-muted-foreground mb-2">Recent Documents</p>
          <Link href="/documents/1" className="flex items-center p-2 rounded-md hover:bg-accent">
            <FileText className="mr-2 h-4 w-4" />
            <span>Sample Document</span>
          </Link>
          <Link href="/documents/2" className="flex items-center p-2 rounded-md hover:bg-accent">
            <FileText className="mr-2 h-4 w-4" />
            <span>Example PDF</span>
          </Link>
        </div>
      </nav>
    </aside>
  )
}
