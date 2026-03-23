import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

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
  
  // Agent API地址 - 直接使用部署的API
  static const String _apiUrl = 'https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site/run';

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _isLoading) return;

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
          text: '请求失败: $e\n\n请检查网络连接',
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
    
    // 构建请求体 - 符合Agent API格式
    final body = jsonEncode({
      'messages': [
        {'role': 'user', 'content': message}
      ]
    });

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: body,
    ).timeout(const Duration(seconds: 120));

    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      
      // 解析响应 - 处理多种可能的格式
      // 格式1: messages数组
      if (data['messages'] != null && data['messages'] is List) {
        final messages = data['messages'] as List;
        for (final msg in messages.reversed) {
          final content = msg['content'];
          if (content != null && msg['type'] != 'human') {
            return content.toString();
          }
        }
      }
      
      // 格式2: output字段
      if (data['output'] != null) {
        return data['output'].toString();
      }
      
      // 格式3: response字段
      if (data['response'] != null) {
        return data['response'].toString();
      }
      
      // 格式4: result字段
      if (data['result'] != null) {
        return data['result'].toString();
      }
      
      // 返回原始响应用于调试
      return '响应格式: ${jsonEncode(data)}';
    } else {
      throw Exception('HTTP ${response.statusCode}');
    }
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

  void _clearChat() {
    setState(() {
      _messages.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('平静 AI'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _clearChat,
            tooltip: '清空对话',
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
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(24),
              ),
              child: Icon(
                Icons.psychology_outlined,
                size: 40,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              '你好，我是平静AI',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              '我可以帮你：',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 16),
            _buildFeatureItem(Icons.search, '搜索网络获取实时信息'),
            _buildFeatureItem(Icons.edit_note, '写文章、翻译、润色文字'),
            _buildFeatureItem(Icons.lightbulb_outline, '解答问题、提供建议'),
            _buildFeatureItem(Icons.code, '编程帮助、代码调试'),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureItem(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 20, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 8),
          Text(text),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage msg) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: msg.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!msg.isUser) ...[
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.psychology,
                size: 18,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: msg.isUser
                    ? Theme.of(context).colorScheme.primary
                    : msg.isError
                        ? Theme.of(context).colorScheme.errorContainer
                        : Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(16),
                  topRight: const Radius.circular(16),
                  bottomLeft: Radius.circular(msg.isUser ? 16 : 4),
                  bottomRight: Radius.circular(msg.isUser ? 4 : 16),
                ),
              ),
              child: SelectableText(
                msg.text,
                style: TextStyle(
                  color: msg.isUser
                      ? Theme.of(context).colorScheme.onPrimary
                      : msg.isError
                          ? Theme.of(context).colorScheme.onErrorContainer
                          : null,
                ),
              ),
            ),
          ),
          if (msg.isUser) ...[
            const SizedBox(width: 8),
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.secondaryContainer,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.person,
                size: 18,
                color: Theme.of(context).colorScheme.secondary,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildLoadingBubble() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primaryContainer,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              Icons.psychology,
              size: 18,
              color: Theme.of(context).colorScheme.primary,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
                bottomLeft: Radius.circular(4),
                bottomRight: Radius.circular(16),
              ),
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
                const SizedBox(width: 12),
                Text(
                  '思考中...',
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: EdgeInsets.fromLTRB(16, 8, 16, MediaQuery.of(context).padding.bottom + 8),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(24),
              ),
              child: TextField(
                controller: _controller,
                maxLines: 4,
                minLines: 1,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _sendMessage(),
                decoration: const InputDecoration(
                  hintText: '输入消息...',
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          FloatingActionButton(
            onPressed: _isLoading ? null : _sendMessage,
            child: Icon(_isLoading ? Icons.hourglass_empty : Icons.send),
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
