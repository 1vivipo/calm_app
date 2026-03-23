import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(const CalmApp());
}

class CalmApp extends StatelessWidget {
  const CalmApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '平静 AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6366F1),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6366F1),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      themeMode: ThemeMode.system,
      home: const ChatPage(),
    );
  }
}

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final _messages = <ChatMessage>[];
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  bool _isLoading = false;
  String _apiUrl = '';
  String _conversationId = '';
  bool _showSettings = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _apiUrl = prefs.getString('api_url') ?? '';
    });
    if (_apiUrl.isEmpty) {
      setState(() => _showSettings = true);
    }
  }

  Future<void> _saveSettings(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('api_url', url);
    setState(() {
      _apiUrl = url;
      _showSettings = false;
    });
  }

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _isLoading) return;

    if (_apiUrl.isEmpty) {
      setState(() => _showSettings = true);
      return;
    }

    _controller.clear();
    setState(() {
      _messages.add(ChatMessage(text: text, isUser: true));
      _isLoading = true;
    });
    _scrollToBottom();

    try {
      final response = await _callAgent(text);
      setState(() {
        _messages.add(ChatMessage(text: response, isUser: false));
      });
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          text: '请求失败: $e\n\n请检查API地址是否正确',
          isUser: false,
          isError: true,
        ));
      });
    } finally {
      setState(() => _isLoading = false);
      _scrollToBottom();
    }
  }

  Future<String> _callAgent(String message) async {
    final uri = Uri.parse(_apiUrl);
    
    // 构建请求体 - 适配Coze API格式
    final body = jsonEncode({
      'conversation_id': _conversationId,
      'messages': [
        {'role': 'user', 'content': message, 'content_type': 'text'}
      ],
      'stream': false,
    });

    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${_extractToken(_apiUrl)}',
      },
      body: body,
    ).timeout(const Duration(seconds: 120));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _conversationId = data['conversation_id'] ?? _conversationId;
      
      // 解析Coze响应格式
      if (data['messages'] != null && data['messages'] is List) {
        final messages = data['messages'] as List;
        for (final msg in messages.reversed) {
          if (msg['role'] == 'assistant' && msg['content'] != null) {
            return msg['content'].toString();
          }
        }
      }
      
      // 备选解析
      if (data['output'] != null) return data['output'].toString();
      if (data['data'] != null && data['data']['output'] != null) {
        return data['data']['output'].toString();
      }
      
      return '收到响应，但格式未知:\n${response.body.substring(0, (response.body.length > 200 ? 200 : response.body.length))}';
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  String _extractToken(String url) {
    // 如果URL中包含token参数，提取它
    final uri = Uri.parse(url);
    return uri.queryParameters['token'] ?? 
           uri.queryParameters['api_key'] ?? 
           'YOUR_API_KEY';
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('平静 AI'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => setState(() => _showSettings = true),
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: () => setState(() {
              _messages.clear();
              _conversationId = '';
            }),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: _messages.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length + (_isLoading ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == _messages.length && _isLoading) {
                        return _buildLoadingBubble();
                      }
                      return _buildMessageBubble(_messages[index]);
                    },
                  ),
          ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.chat_bubble_outline_rounded,
            size: 64,
            color: Theme.of(context).colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            '开始对话吧',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              color: Theme.of(context).colorScheme.outline,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '我可以帮你搜索网络、回答问题、写代码...',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Theme.of(context).colorScheme.outline,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage msg) {
    return Align(
      alignment: msg.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.all(12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.8,
        ),
        decoration: BoxDecoration(
          color: msg.isUser
              ? Theme.of(context).colorScheme.primaryContainer
              : msg.isError
                  ? Theme.of(context).colorScheme.errorContainer
                  : Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(16),
        ),
        child: SelectableText(
          msg.text,
          style: TextStyle(
            color: msg.isUser
                ? Theme.of(context).colorScheme.onPrimaryContainer
                : msg.isError
                    ? Theme.of(context).colorScheme.onErrorContainer
                    : Theme.of(context).colorScheme.onSurface,
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingBubble() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              '思考中...',
              style: TextStyle(
                color: Theme.of(context).colorScheme.onSurface,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 8,
        bottom: MediaQuery.of(context).padding.bottom + 8,
      ),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _controller,
              maxLines: 4,
              minLines: 1,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _sendMessage(),
              decoration: InputDecoration(
                hintText: '输入消息...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          IconButton.filled(
            onPressed: _isLoading ? null : _sendMessage,
            icon: const Icon(Icons.send),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }
}

class ChatMessage {
  final String text;
  final bool isUser;
  final bool isError;

  ChatMessage({
    required this.text,
    required this.isUser,
    this.isError = false,
  });
}
