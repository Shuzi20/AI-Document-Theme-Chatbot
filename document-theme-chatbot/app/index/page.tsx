"use client";

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Upload } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

export default function HomePage() {
  const [question, setQuestion] = useState('');
  const [responses, setResponses] = useState<any[]>([]);

  const handleAsk = async () => {
    if (!question.trim()) return;

    const res = await fetch('http://localhost:8000/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, top_k: 5 }),
    });

    const data = await res.json();
    setResponses([{ question, ...data }, ...responses]);
    setQuestion('');
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) {
      console.warn("No files selected.");
      return;
    }

    const formData = new FormData();

    Array.from(e.target.files).forEach((file) => {
      console.log("[UPLOAD] Selected:", file.name);
      formData.append('files', file); // ✅ key must match backend
    });

    try {
      const res = await fetch('http://localhost:8000/upload/', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        console.error("[UPLOAD] Server returned error:", res.statusText);
        return;
      }

      const result = await res.json();
      console.log('[UPLOAD] Success:', result);
    } catch (error) {
      console.error("[UPLOAD] Failed:", error);
    }
  };



  return (
    <div className="flex h-screen">
      {/* Left Sidebar for Filters */}
      <div className="w-64 bg-gray-100 p-4 border-r">
        <h2 className="text-lg font-semibold mb-4">Filters</h2>

        <div className="space-y-4 text-sm">
          {/* Date Filter */}
          <div>
            <label className="font-medium block mb-1">Date</label>
            <input type="date" className="w-full px-2 py-1 border rounded" />
          </div>

          {/* Author Filter */}
          <div>
            <label className="font-medium block mb-1">Author</label>
            <input type="text" placeholder="Enter author" className="w-full px-2 py-1 border rounded" />
          </div>

          {/* Document Type Filter */}
          <div>
            <label className="font-medium block mb-1">Document Type</label>
            <select className="w-full px-2 py-1 border rounded">
              <option>All</option>
              <option>Legal</option>
              <option>Report</option>
              <option>Policy</option>
            </select>
          </div>

          {/* Relevance Filter */}
          <div>
            <label className="font-medium block mb-1">Sort By</label>
            <select className="w-full px-2 py-1 border rounded">
              <option>Relevance</option>
              <option>Newest</option>
              <option>Oldest</option>
            </select>
          </div>

          {/* Exclude Docs */}
          <div className="flex items-center gap-2 mt-2">
            <input type="checkbox" id="exclude" className="accent-black" />
            <label htmlFor="exclude">Exclude specific documents</label>
          </div>
        </div>
      </div>


      {/* Chat + Input Area */}
      <div className="flex-1 relative flex flex-col">
        {/* Chat Output */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 pb-28">
          {responses.map((res, idx) => (
            <div key={idx} className="space-y-2">
              <p className="font-medium">🧑‍💻 You: {res.question}</p>
              <Card>
                <CardContent className="p-4 space-y-2">
                  <p className="font-semibold">📚 Top Chunks:</p>
                  <ul className="list-disc ml-6 text-sm">
                    {Array.isArray(res.top_chunks) && res.top_chunks.length > 0 ? (
                      res.top_chunks.map((c: any, i: number) => (
                        <li key={i}>
                          <strong>{c.metadata.doc_name}, Page {c.metadata.page}:</strong> {c.text}
                        </li>
                      ))
                    ) : (
                      <li className="text-gray-500 italic">No relevant document chunks found for this query.</li>
                    )}
                  </ul>

                  <p className="font-semibold">🧠 Theme Summary:</p>
                  <p className="text-sm whitespace-pre-wrap">{res.theme_summary}</p>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>

        {/* Fixed Input Bar at Bottom of Chat Panel */}
        <div className="absolute bottom-0 left-0 right-0 bg-white border-t p-4 flex items-center gap-2">
          {/* This label triggers the hidden file input via htmlFor */}
          <label htmlFor="upload" className="cursor-pointer">
            <Upload className="h-5 w-5 text-gray-500" />
          </label>

          {/* ✅ Connect this input with the label above using the same id */}
          <input
            id="upload" // <-- Required so label can trigger this
            type="file"
            multiple
            onChange={handleUpload}
            className="hidden"
          />

          <Input
            placeholder="Ask your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="flex-1"
          />
          <Button onClick={handleAsk}>Ask</Button>
        </div>
      </div>
    </div>
  );
}
