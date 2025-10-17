"use client";

import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
}

export function ChatMessages({ messages, isLoading }: ChatMessagesProps) {
  return (
    <div className="space-y-6">
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn(
            "flex gap-4 animate-slide-in",
            message.role === "user" ? "justify-end" : "justify-start"
          )}
        >
          {message.role === "assistant" && (
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-primary">
              <Bot className="h-5 w-5 text-primary-foreground" />
            </div>
          )}
          <div
            className={cn(
              "max-w-[80%] rounded-lg px-4 py-3 overflow-hidden",
              message.role === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-muted"
            )}
          >
            <div>
              <ReactMarkdown 
                rehypePlugins={[rehypeRaw]}
                className="prose prose-sm dark:prose-invert max-w-none break-words prose-headings:font-semibold prose-h3:text-base prose-h3:mt-4 prose-h3:mb-2 prose-p:my-2 prose-ul:my-2 prose-li:my-1"
                components={{
                img: ({node, src, alt, ...props}) => {
                  if (!src) {
                    console.error('❌ Image src is missing');
                    return null;
                  }

                  console.log('🖼️ Rendering image:', { 
                    alt,
                    srcLength: src.length, 
                    srcPreview: src.substring(0, 60),
                    isPNG: src.includes('data:image/png;base64,iVBORw0KG')
                  });

                  return (
                    <div className="my-4">
                      <img 
                        src={src}
                        alt={alt || 'Chart'}
                        {...props} 
                        className="max-w-full h-auto rounded-lg shadow-lg bg-white p-4"
                        style={{maxHeight: '600px', objectFit: 'contain', display: 'block', margin: '0 auto'}}
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          console.error('❌ Image failed to load:', {
                            alt,
                            srcLength: src?.length,
                            srcStart: src?.substring(0, 100)
                          });
                        }}
                        onLoad={() => console.log('✅ Image loaded:', alt)}
                      />
                    </div>
                  );
                },
                pre: ({node, ...props}) => (
                  <pre {...props} className="overflow-x-auto text-xs bg-gray-100 dark:bg-gray-900 p-3 rounded-lg my-3 border border-gray-200 dark:border-gray-700" />
                ),
                code: ({node, ...props}) => (
                  <code {...props} className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded break-all font-mono" />
                ),
                table: ({node, ...props}) => (
                  <div className="overflow-x-auto my-4">
                    <table {...props} className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 text-xs" />
                  </div>
                ),
                thead: ({node, ...props}) => (
                  <thead {...props} className="bg-gray-50 dark:bg-gray-800" />
                ),
                tbody: ({node, ...props}) => (
                  <tbody {...props} className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700" />
                ),
                tr: ({node, ...props}) => (
                  <tr {...props} className="hover:bg-gray-50 dark:hover:bg-gray-800" />
                ),
                th: ({node, ...props}) => (
                  <th {...props} className="px-3 py-2 text-left font-semibold text-gray-900 dark:text-gray-100" />
                ),
                td: ({node, ...props}) => (
                  <td {...props} className="px-3 py-2 text-gray-700 dark:text-gray-300" />
                ),
                hr: ({node, ...props}) => (
                  <hr {...props} className="my-4 border-gray-200 dark:border-gray-700" />
                )
              }}
            >
              {message.content}
            </ReactMarkdown>
            
            {/* Render images separately */}
            {message.images && message.images.length > 0 && (
              <div className="mt-4 space-y-4">
                {message.images.map((img, idx) => {
                  const imgSrc = `data:image/png;base64,${img}`;
                  return (
                    <div key={idx} className="relative group">
                      <img 
                        src={imgSrc}
                        alt={`Chart ${idx + 1}`}
                        className="max-w-full h-auto rounded-lg shadow-lg bg-white p-4 cursor-pointer transition-transform hover:scale-[1.02]"
                        style={{maxHeight: '600px', objectFit: 'contain', display: 'block', margin: '0 auto'}}
                        onClick={() => {
                          // Open in new tab for fullscreen view
                          const win = window.open();
                          if (win) {
                            win.document.write(`
                              <html>
                                <head>
                                  <title>Chart ${idx + 1}</title>
                                  <style>
                                    body { margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #000; }
                                    img { max-width: 100%; max-height: 100vh; object-fit: contain; }
                                  </style>
                                </head>
                                <body>
                                  <img src="${imgSrc}" alt="Chart ${idx + 1}" />
                                </body>
                              </html>
                            `);
                          }
                        }}
                        onError={() => console.error(`❌ Failed to load image ${idx + 1}`)}
                        onLoad={() => console.log(`✅ Image ${idx + 1} loaded successfully`)}
                      />
                      {/* Hover overlay with actions */}
                      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            // Download image
                            const link = document.createElement('a');
                            link.href = imgSrc;
                            link.download = `chart-${idx + 1}.png`;
                            link.click();
                          }}
                          className="bg-white/90 hover:bg-white text-gray-800 p-2 rounded-lg shadow-lg transition-colors"
                          title="Download chart"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="7 10 12 15 17 10"></polyline>
                            <line x1="12" y1="15" x2="12" y2="3"></line>
                          </svg>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            // Open in new tab
                            const win = window.open();
                            if (win) {
                              win.document.write(`
                                <html>
                                  <head>
                                    <title>Chart ${idx + 1}</title>
                                    <style>
                                      body { margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f5f5f5; }
                                      img { max-width: 95%; max-height: 95vh; object-fit: contain; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                                    </style>
                                  </head>
                                  <body>
                                    <img src="${imgSrc}" alt="Chart ${idx + 1}" />
                                  </body>
                                </html>
                              `);
                            }
                          }}
                          className="bg-white/90 hover:bg-white text-gray-800 p-2 rounded-lg shadow-lg transition-colors"
                          title="Open in new tab"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                            <polyline points="15 3 21 3 21 9"></polyline>
                            <line x1="10" y1="14" x2="21" y2="3"></line>
                          </svg>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
          </div>
          {message.role === "user" && (
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-secondary">
              <User className="h-5 w-5" />
            </div>
          )}
        </div>
      ))}
      {isLoading && (
        <div className="flex gap-4 animate-slide-in">
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-primary">
            <Bot className="h-5 w-5 text-primary-foreground" />
          </div>
          <div className="max-w-[80%] rounded-lg bg-muted px-4 py-3">
            <div className="flex gap-1">
              <div className="h-2 w-2 animate-pulse rounded-full bg-foreground/50" />
              <div className="h-2 w-2 animate-pulse rounded-full bg-foreground/50 [animation-delay:0.2s]" />
              <div className="h-2 w-2 animate-pulse rounded-full bg-foreground/50 [animation-delay:0.4s]" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
