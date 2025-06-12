"use client";

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Upload } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

export default function HomePage() {
  const [question, setQuestion] = useState('');
  const [responses, setResponses] = useState<any[]>([]);
  const [documents, setDocuments] = useState<string[]>([]);
  const [excludeMode, setExcludeMode] = useState(false);
  const [excludedDocs, setExcludedDocs] = useState<string[]>([]);
  const [modalContent, setModalContent] = useState<{ title: string; text: string } | null>(null);
  const [expandedRow, setExpandedRow] = useState<number | null>(null);
  const [matchedDocs, setMatchedDocs] = useState<{ doc_id: string; doc_name: string }[]>([]);

  //  Moved outside so it's globally usable
  const fetchDocs = async () => {
    const res = await fetch('http://localhost:8000/documents');
    const data = await res.json();
    setDocuments(data);
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem('chatHistory');
    if (saved) setResponses(JSON.parse(saved));
  }, []);

  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(responses));
  }, [responses]);


  const handleAsk = async () => {
    if (!question.trim()) return;

    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          excluded_docs: excludeMode ? excludedDocs : [],
        }),
      });

      const data = await res.json();

      // ✅ Extract unique doc_id + doc_name pairs
      const matchedDocsSet = new Map<string, { doc_id: string; doc_name: string }>();
      (data.document_answers as any[]).forEach((d) => {
        matchedDocsSet.set(d.doc_id, { doc_id: d.doc_id, doc_name: d.doc_name });
      });
      setMatchedDocs(Array.from(matchedDocsSet.values()));

      // ✅ Update chat state and reset input
      setResponses([...responses, { question, ...data }]);
      setQuestion('');
    } catch (error) {
      console.error("Failed to get response:", error);
    }
  };



  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;

    const formData = new FormData();
    Array.from(e.target.files).forEach((file) => {
      formData.append('files', file);
    });

    try {
      const res = await fetch('http://localhost:8000/upload/', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) return;
      await fetchDocs(); // ✅ this now works
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  const toggleExcluded = (doc: string) => {
    setExcludedDocs((prev) =>
      prev.includes(doc) ? prev.filter((d) => d !== doc) : [...prev, doc]
    );
  };

  const openChunkModal = (doc: string, page: string, chunk: string, text: string) => {
    setModalContent({
      title: `${doc} – Page ${page}, Chunk ${chunk}`,
      text,
    });
  };
  

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div className="w-64 bg-gray-100 p-4 border-r overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4">Filters</h2>

        <div className="space-y-4 text-sm">
          <div>
            <label className="font-medium block mb-1">Date</label>
            <input type="date" className="w-full px-2 py-1 border rounded" />
          </div>
          <div>
            <label className="font-medium block mb-1">Author</label>
            <input type="text" placeholder="Enter author" className="w-full px-2 py-1 border rounded" />
          </div>
          <div>
            <label className="font-medium block mb-1">Document Type</label>
            <select className="w-full px-2 py-1 border rounded">
              <option>All</option>
              <option>Legal</option>
              <option>Report</option>
              <option>Policy</option>
            </select>
          </div>
          <div>
            <label className="font-medium block mb-1">Sort By</label>
            <select className="w-full px-2 py-1 border rounded">
              <option>Relevance</option>
              <option>Newest</option>
              <option>Oldest</option>
            </select>
          </div>

          <div className="flex items-center gap-2 mt-2">
            <input
              type="checkbox"
              id="exclude"
              className="accent-black"
              checked={excludeMode}
              onChange={(e) => setExcludeMode(e.target.checked)}
            />
            <label htmlFor="exclude">Exclude specific documents</label>
          </div>

          {excludeMode && (
            <div>
              <h3 className="font-semibold mt-3">Docs to Exclude:</h3>
              <ul className="mt-1 space-y-1 text-sm max-h-40 overflow-y-auto pr-1">
                {documents.map((doc, i) => (
                  <li key={i}>
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={excludedDocs.includes(doc)}
                        onChange={() => toggleExcluded(doc)}
                        className="accent-black"
                      />
                      <span className="truncate" title={doc}>{doc}</span>
                    </label>
                  </li>
                ))}
              </ul>
            </div>
          )}

        </div>
      </div>

      {/* Main Panel */}
      <div className="flex-1 relative flex flex-col">
        {/* Output */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 pb-28">
          {responses.reverse().map((res, idx) => (
            <div key={idx} className="space-y-2">
              <p className="font-medium">🧑‍💻 You: {res.question}</p>
              <Card>
                <CardContent className="p-4 space-y-2">
                  {/* 📊 Document Answers Table */}
                  <p className="font-semibold">📊 Document Answers:</p>
                  <div className="overflow-x-auto">
                    <table className="w-full border text-sm">
                      <thead className="bg-gray-100">
                        <tr>
                          <th className="border px-2 py-1 text-left">Document ID</th>
                          <th className="border px-2 py-1 text-left">Extracted Answer</th>
                          <th className="border px-2 py-1 text-left">Citation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {res.document_answers.map((d: any, i: number) => (
                          <tr key={i} className="align-top">
                            <td className="border px-2 py-1 font-medium">{d.doc_id}</td>
                            <td className="border px-2 py-1">
                              <div className="max-w-md text-sm">
                                {expandedRow === i ? (
                                  <>
                                    {d.answer}
                                    <button onClick={() => setExpandedRow(null)} className="text-blue-600 ml-2">Show less</button>
                                  </>
                                ) : (
                                  <>
                                    {d.answer.slice(0, 150)}...
                                    <button onClick={() => setExpandedRow(i)} className="text-blue-600 ml-2">Show more</button>
                                  </>
                                )}
                              </div>
                            </td>
                            <td className="border px-2 py-1">{d.citation}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* 🧠 Theme Summary */}
                  <p className="font-semibold pt-4">🧠 Synthesized Answer (Themes):</p>
                  <p className="text-sm whitespace-pre-wrap">
                    {res.theme_summary.split(/(\[.*?\])/).map((part: string, i: number) => {
                      const match = part.match(/\[(.*?), Page (.*?), Chunk (.*?)\]/);
                      if (match) {
                        const [_, doc, page, chunk] = match;
                        const chunkMatch = res.document_answers.find(
                          (c: any) =>
                            c.doc_id === doc &&
                            c.citation.includes(`Page ${page}`) &&
                            c.citation.includes(`Chunk ${chunk}`)
                        );
                        return (
                          <button
                            key={i}
                            onClick={() => {
                              if (chunkMatch) {
                                openChunkModal(doc, page, chunk, chunkMatch.answer);
                              }
                            }}
                            className="text-blue-600 underline hover:text-blue-800 mx-1"
                          >
                            {part}
                          </button>
                        );
                      } else {
                        return <span key={i}>{part}</span>;
                      }
                    })}
                  </p>

                  {/* 📄 Matched Document Names */}
                  {res.document_answers?.length > 0 && (
                    <div className="mt-3 text-sm text-gray-700">
                      Matched documents from this query:
                      <ul className="list-disc ml-4 mt-1">
                        {[...new Map(res.document_answers.map((doc: any) => [doc.doc_id, doc])).values()].map((doc: any, idx: number) => (
                          <li key={idx}>
                            <span className="font-medium">{doc.doc_id}</span> – {doc.doc_name}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}


                </CardContent>
              </Card>

            </div>
          ))}
        </div>

        {/* Input Bar */}
        <div className="absolute bottom-0 left-0 right-0 bg-white border-t p-4 flex items-center gap-2">
          <label htmlFor="upload" className="cursor-pointer">
            <Upload className="h-5 w-5 text-gray-500" />
          </label>
          <input
            id="upload"
            type="file"
            multiple
            onChange={handleUpload}
            className="hidden"
          />
          <Input
            placeholder="Ask your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAsk();
              }
            }}
            className="flex-1"
          />
          <Button onClick={handleAsk}>Ask</Button>
        </div>
      </div>

      {/* 🔍 Modal Viewer */}
      {modalContent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white max-w-xl w-full rounded shadow-lg p-6 space-y-4">
            <h2 className="text-lg font-semibold">{modalContent.title}</h2>
            <p className="text-sm whitespace-pre-wrap">{modalContent.text}</p>
            <div className="text-right">
              <Button variant="secondary" onClick={() => setModalContent(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
