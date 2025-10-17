import { useState, useCallback, useEffect } from "react";
import { useChatStore } from "@/store/chat-store";
import { queryApi, api } from "@/lib/api";
import { wsService } from "@/lib/websocket";
import { useToast } from "@/hooks/use-toast";

export function useChat() {
  const { messages, addMessage, setIsLoading, isLoading, currentFile } = useChatStore();
  const { toast } = useToast();
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const socket = wsService.connect();
    
    // Socket.io is disabled, so socket will be null
    // Use REST API fallback instead
    if (!socket) {
      setIsConnected(false);
      return;
    }
    
    socket.on("connect", () => setIsConnected(true));
    socket.on("disconnect", () => setIsConnected(false));
    
    socket.on("message", (data: any) => {
      addMessage({
        role: "assistant",
        content: data.content || data.message,
        fileId: data.fileId,
      });
      setIsLoading(false);
    });

    socket.on("error", (error: any) => {
      toast({
        title: "Error",
        description: error.message || "An error occurred",
        variant: "destructive",
      });
      setIsLoading(false);
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("message");
      socket.off("error");
    };
  }, [addMessage, setIsLoading, toast]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      addMessage({ role: "user", content });
      setIsLoading(true);

      try {
        if (isConnected) {
          wsService.emit("chat", {
            message: content,
            fileId: currentFile?.id,
          });
        } else {
          // Use REST API fallback
          const fileId = currentFile?.id ? Number(currentFile.id) : undefined;
          const response = await queryApi.ask(content, fileId);
          
          console.log('API Response:', response.data);
          
          // If code was generated, execute it automatically
          if (response.data.code && response.data.success) {
            try {
              // Show initial message
              addMessage({
                role: "assistant",
                content: "🔄 Analyzing your data and generating visualizations...",
              });
              
              // Execute the generated code
              const execResponse = await api.post('/exec/execute', {
                code: response.data.code,
                file_id: fileId,
                timeout_seconds: 60,
                max_memory_mb: 512
              });
              
              console.log('🔍 Full Execution Response:', execResponse);
              console.log('🔍 Response data:', execResponse.data);
              console.log('🔍 Response data keys:', Object.keys(execResponse.data));
              console.log('🔍 Images field exists?', 'images' in execResponse.data);
              console.log('🔍 Images array:', execResponse.data.images);
              console.log('🔍 Images array length:', execResponse.data.images?.length || 0);
              if (execResponse.data.images && execResponse.data.images.length > 0) {
                console.log('🔍 First image type:', typeof execResponse.data.images[0]);
                console.log('🔍 First image length:', execResponse.data.images[0]?.length);
                console.log('🔍 First image preview (first 100 chars):', execResponse.data.images[0]?.substring(0, 100));
              }
              
              // Check if execution was successful
              if (!execResponse.data.success) {
                addMessage({
                  role: "assistant",
                  content: `❌ Execution failed: ${execResponse.data.error || 'Unknown error'}`,
                });
                setIsLoading(false);
                return;
              }
              
              // Build final response with results
              let finalResponse = '';
              
              // 1. Code Explanation Section (like Julius AI)
              if (execResponse.data.code) {
                finalResponse += '### 🐍 Python Code\n\n';
                finalResponse += '```python\n' + execResponse.data.code + '\n```\n\n';
                if (response.data.explanation) {
                  finalResponse += '**Code Explanation:** ' + response.data.explanation + '\n\n';
                }
              }
              
              // 2. Dataset Preview Section (like Julius AI)
              if (execResponse.data.data_preview) {
                const preview = execResponse.data.data_preview;
                finalResponse += '### 📋 Quick look at your dataset\n\n';
                finalResponse += `**Dataset shape:** (${preview.shape[0]} rows × ${preview.shape[1]} columns)\n\n`;
                
                // Show columns
                finalResponse += '**Columns:** `' + preview.columns.join('`, `') + '`\n\n';
                
                // Show first few rows as a properly formatted table
                if (preview.head && preview.head.length > 0) {
                  const headers = preview.columns;
                  
                  // Table header
                  finalResponse += '| ' + headers.join(' | ') + ' |\n';
                  finalResponse += '|' + headers.map(() => ' --- ').join('|') + '|\n';
                  
                  // Table rows
                  preview.head.slice(0, 5).forEach((row: any) => {
                    const values = headers.map((h: string) => {
                      const val = row[h];
                      if (val === null || val === undefined) return 'NaN';
                      // Format numbers nicely
                      if (typeof val === 'number') {
                        return val % 1 === 0 ? val.toString() : val.toFixed(2);
                      }
                      return String(val);
                    });
                    finalResponse += '| ' + values.join(' | ') + ' |\n';
                  });
                  finalResponse += '\n';
                }
              }
              
              // 3. Text Output Section
              if (execResponse.data.output && execResponse.data.output.trim()) {
                finalResponse += '### 📊 Analysis Results\n\n```\n' + execResponse.data.output.trim() + '\n```\n\n';
              }
              
              // 4. Visualizations Section (like Julius AI)
              if (execResponse.data.images && execResponse.data.images.length > 0) {
                console.log('📊 Processing images:', execResponse.data.images.length);
                console.log('📊 Raw images data:', execResponse.data.images);
                finalResponse += '### 📈 Visualizations\n\n';
                
                execResponse.data.images.forEach((img: string, idx: number) => {
                  if (img && img.length > 0) {
                    const cleanImg = img.replace(/\s/g, '');
                    console.log(`Chart ${idx + 1}:`, {
                      originalLength: img.length,
                      cleanedLength: cleanImg.length,
                      startsWithPNG: cleanImg.startsWith('iVBORw0KG'),
                      first50: cleanImg.substring(0, 50)
                    });
                    
                    // Use a special marker that we'll replace with actual images
                    finalResponse += `__IMAGE_PLACEHOLDER_${idx}__\n\n`;
                  } else {
                    console.warn(`Chart ${idx + 1} is empty or invalid`);
                  }
                });
              } else {
                console.warn('⚠️ No images in execResponse.data.images');
              }
              
              // 5. Follow-up Questions Section (like Julius AI)
              if (response.data.follow_up_questions && response.data.follow_up_questions.length > 0) {
                finalResponse += '---\n\n### 💡 Suggested Follow-up Questions\n\n';
                response.data.follow_up_questions.forEach((question: string) => {
                  finalResponse += `- ${question}\n`;
                });
                finalResponse += '\n';
              }
              
              if (!finalResponse.trim()) {
                finalResponse = '✅ Analysis completed successfully.';
              }
              
              // Debug: Log the final response
              console.log('📝 Final response length:', finalResponse.length);
              console.log('📝 Final response contains <img>:', finalResponse.includes('<img'));
              console.log('📝 Contains base64:', finalResponse.includes('data:image/png;base64,'));
              console.log('📝 Number of <img> tags:', (finalResponse.match(/<img/g) || []).length);
              
              // Log a sample of the response around images
              const imgIndex = finalResponse.indexOf('<img');
              if (imgIndex !== -1) {
                console.log('📝 Image tag sample:', finalResponse.substring(imgIndex, imgIndex + 200));
              }
              
              // Store images separately
              const imageData = execResponse.data.images?.map((img: string) => img.replace(/\s/g, '')) || [];
              
              // Update the message with results
              addMessage({
                role: "assistant",
                content: finalResponse.trim(),
                images: imageData, // Pass images separately
              });
              
            } catch (execError: any) {
              console.error('Execution error:', execError);
              console.error('Error response:', execError.response);
              console.error('Error status:', execError.response?.status);
              console.error('Error data:', execError.response?.data);
              
              const errorMsg = execError.response?.data?.detail || 
                              execError.response?.data?.error ||
                              execError.response?.statusText ||
                              execError.message || 
                              'Unknown error occurred';
              addMessage({
                role: "assistant",
                content: `❌ Execution failed: ${errorMsg}\n\nStatus: ${execError.response?.status || 'N/A'}\n\n${response.data.explanation || ''}`,
              });
            }
          } else {
            // No code to execute, just show explanation
            const aiResponse = response.data.explanation || 
                              response.data.error || 
                              'Analysis complete.';
            
            addMessage({
              role: "assistant",
              content: aiResponse,
            });
          }
          
          setIsLoading(false);
        }
      } catch (error: any) {
        toast({
          title: "Error",
          description: error.response?.data?.detail || "Failed to send message",
          variant: "destructive",
        });
        setIsLoading(false);
      }
    },
    [addMessage, setIsLoading, isLoading, currentFile, isConnected, toast]
  );

  return {
    messages,
    sendMessage,
    isLoading,
    isConnected,
  };
}
