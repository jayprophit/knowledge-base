import React, { useState, useEffect } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  TextInput, 
  TouchableOpacity,
  FlatList,
  ScrollView,
  SafeAreaView,
  ActivityIndicator,
  Platform 
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';
import MultimodalCapture from './MultimodalCapture';

// API Base URL - change for production
const API_BASE = "http://192.168.1.100:8000"; // Update with your dev machine IP or production URL

// Simplified API client
const api = {
  fetchCategories: async () => {
    try {
      const response = await fetch(`${API_BASE}/categories`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error fetching categories:", error);
      return { categories: [] };
    }
  },
  
  searchKnowledgeBase: async (query) => {
    try {
      const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error searching:", error);
      return { results: [] };
    }
  },
  
  generateCode: async (prompt, language) => {
    try {
      const response = await fetch(`${API_BASE}/generate_code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, language })
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error generating code:", error);
      return { code: "Error generating code" };
    }
  }
};

// Message component
const Message = ({ message, isUser }) => (
  <View style={[styles.message, isUser ? styles.userMessage : styles.assistantMessage]}>
    <View style={styles.messageAvatar}>
      <Text style={styles.avatarText}>{isUser ? '👤' : '🤖'}</Text>
    </View>
    <View style={styles.messageContent}>
      <Text style={styles.messageText}>{message.content}</Text>
    </View>
  </View>
);

export default function App() {
  const [messages, setMessages] = useState([{
    id: 1,
    role: 'assistant',
    content: 'Hello! I\'m your AI assistant. How can I help you today?',
    timestamp: new Date().toISOString()
  }]);
  const [inputText, setInputText] = useState('');
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat'); // 'chat', 'code', 'categories', 'multimodal'
  const [multimodalResult, setMultimodalResult] = useState(null);

  // Fetch categories on component mount
  useEffect(() => {
    async function loadCategories() {
      const data = await api.fetchCategories();
      setCategories(data.categories || []);
    }
    loadCategories();
  }, []);

  const handleSend = async () => {
    if (!inputText.trim()) return;
    
    // Add user message
    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: inputText,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    
    // Search knowledge base
    const searchResults = await api.searchKnowledgeBase(inputText);
    
    // Create assistant response
    let assistantContent = "No results found in the knowledge base.";
    if (searchResults.results && searchResults.results.length > 0) {
      assistantContent = `Knowledge Base Results:\n\n${
        searchResults.results.map(r => `${r.file}\n${r.snippet || 'No preview'}`).join('\n\n')
      }`;
    }
    
    const assistantMessage = {
      id: messages.length + 2,
      role: 'assistant',
      content: assistantContent,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, assistantMessage]);
    setIsLoading(false);
  };

  // Code generation function
  const [codePrompt, setCodePrompt] = useState('');
  const [codeLanguage, setCodeLanguage] = useState('python');
  const [generatedCode, setGeneratedCode] = useState(null);
  
  const handleGenerateCode = async () => {
    if (!codePrompt.trim()) return;
    
    setIsLoading(true);
    const result = await api.generateCode(codePrompt, codeLanguage);
    setGeneratedCode(result.code || 'Error generating code');
    setIsLoading(false);
  };

  // Render functions for different tabs
  function renderChatTab() {
    return (
      <>
        <FlatList
          data={messages}
          keyExtractor={item => item.id.toString()}
          renderItem={({ item }) => (
            <Message message={item} isUser={item.role === 'user'} />
          )}
          style={styles.messageList}
        />
        
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Ask me anything..."
            multiline
          />
          <TouchableOpacity 
            style={[styles.sendButton, !inputText.trim() && styles.disabledButton]} 
            onPress={handleSend}
            disabled={!inputText.trim() || isLoading}
          >
            <Text style={styles.sendButtonText}>Send</Text>
          </TouchableOpacity>
        </View>
      </>
    );
  };
  
  function renderCodeTab() {
    return (
      <ScrollView style={styles.codeTabContainer}>
        <Text style={styles.sectionTitle}>AI Code Generation</Text>
        
        <TextInput
          style={styles.codeInput}
          value={codePrompt}
          onChangeText={setCodePrompt}
          placeholder="Describe what code you want to generate..."
          multiline
        />
        
        <View style={styles.codeOptionsRow}>
          <View style={styles.pickerContainer}>
            <Text>Language:</Text>
            {/* In a real app, use a proper dropdown/picker component */}
            <TouchableOpacity style={styles.pickerButton}>
              <Text>{codeLanguage}</Text>
            </TouchableOpacity>
          </View>
          
          <TouchableOpacity 
            style={[styles.generateButton, (!codePrompt.trim() || isLoading) && styles.disabledButton]} 
            onPress={handleGenerateCode}
            disabled={!codePrompt.trim() || isLoading}
          >
            <Text style={styles.buttonText}>Generate</Text>
          </TouchableOpacity>
        </View>
        
        {generatedCode && (
          <View style={styles.codeResultContainer}>
            <Text style={styles.codeResultText}>{generatedCode}</Text>
          </View>
        )}
      </ScrollView>
    );
  };
  
  function renderCategoriesTab() {
    return (
      <View style={styles.categoriesTabContainer}>
        <Text style={styles.sectionTitle}>Knowledge Base Categories</Text>
        <FlatList
          data={categories}
          keyExtractor={(item) => item}
          renderItem={({ item }) => (
            <View style={styles.categoryItem}>
              <Text style={styles.categoryIcon}>📚</Text>
              <Text style={styles.categoryName}>{item}</Text>
            </View>
          )}
        />
      </View>
    );
  }

  function renderMultimodalTab() {
    return (
      <View style={{ flex: 1 }}>
        <MultimodalCapture onResult={setMultimodalResult} />
        {multimodalResult && (
          <View style={{ padding: 16 }}>
            <Text style={{ fontWeight: 'bold', color: '#1a73e8', marginBottom: 4 }}>Latest Analysis Result:</Text>
            <Text style={{ color: '#333', fontSize: 14 }}>{JSON.stringify(multimodalResult, null, 2)}</Text>
          </View>
        )}
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Knowledge Base Assistant</Text>
      </View>
      
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'chat' && styles.activeTab]}
          onPress={() => setActiveTab('chat')}
        >
          <Text style={[styles.tabText, activeTab === 'chat' && styles.activeTabText]}>Chat</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'code' && styles.activeTab]}
          onPress={() => setActiveTab('code')}
        >
          <Text style={[styles.tabText, activeTab === 'code' && styles.activeTabText]}>Code</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'categories' && styles.activeTab]}
          onPress={() => setActiveTab('categories')}
        >
          <Text style={[styles.tabText, activeTab === 'categories' && styles.activeTabText]}>Categories</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'multimodal' && styles.activeTab]}
          onPress={() => setActiveTab('multimodal')}
        >
          <Text style={[styles.tabText, activeTab === 'multimodal' && styles.activeTabText]}>Multimodal</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.content}>
        {isLoading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color="#1a73e8" />
          </View>
        )}
        
        {activeTab === 'chat' && renderChatTab()}
        {activeTab === 'code' && renderCodeTab()}
        {activeTab === 'categories' && renderCategoriesTab()}
        {activeTab === 'multimodal' && renderMultimodalTab()}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7f8fa',
  },
  header: {
    backgroundColor: '#fff',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  tab: {
    flex: 1,
    padding: 12,
    alignItems: 'center',
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: '#1a73e8',
  },
  tabText: {
    color: '#555',
  },
  activeTabText: {
    color: '#1a73e8',
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    position: 'relative',
  },
  messageList: {
    flex: 1,
    padding: 16,
  },
  message: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  userMessage: {
    justifyContent: 'flex-end',
  },
  assistantMessage: {
    justifyContent: 'flex-start',
  },
  messageAvatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#e1e1e1',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    fontSize: 18,
  },
  messageContent: {
    maxWidth: '80%',
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 12,
    marginHorizontal: 8,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 1,
      },
      android: {
        elevation: 1,
      },
    }),
  },
  messageText: {
    fontSize: 16,
    color: '#333',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  input: {
    flex: 1,
    backgroundColor: '#f1f3f4',
    borderRadius: 24,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 16,
    maxHeight: 100,
  },
  sendButton: {
    marginLeft: 8,
    backgroundColor: '#1a73e8',
    width: 60,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  disabledButton: {
    backgroundColor: '#b3c7e6',
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(255, 255, 255, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 100,
  },
  // Code tab styles
  codeTabContainer: {
    flex: 1,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333',
  },
  codeInput: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    minHeight: 100,
    fontSize: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  codeOptionsRow: {
    flexDirection: 'row',
    marginBottom: 16,
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  pickerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  pickerButton: {
    marginLeft: 8,
    backgroundColor: '#f1f3f4',
    padding: 8,
    borderRadius: 4,
    minWidth: 100,
    alignItems: 'center',
  },
  generateButton: {
    backgroundColor: '#1a73e8',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  codeResultContainer: {
    backgroundColor: '#282c34',
    borderRadius: 8,
    padding: 16,
  },
  codeResultText: {
    color: '#fff',
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
  },
  // Categories tab styles
  categoriesTabContainer: {
    flex: 1,
    padding: 16,
  },
  categoryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 1,
      },
      android: {
        elevation: 1,
      },
    }),
  },
  categoryIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  categoryName: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
});
