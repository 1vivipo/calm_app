import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:permission_handler/permission_handler.dart';

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

// 模型类型 - 与后端对齐
enum ModelType {
  mini('Mini快速', 'doubao-seed-1-6-lite-251015', Icons.bolt, '快速响应，适合简单对话', 30),
  pro('Pro思考', 'doubao-seed-1-6-251015', Icons.psychology, '平衡性能，适合复杂问题', 60),
  agent('Agent专家', 'doubao-seed-1-8-251228', Icons.smart_toy, '工具调用，画图/搜索/代码', 120);

  final String label;
  final String modelId;
  final IconData icon;
  final String description;
  final int timeoutSeconds;
  const ModelType(this.label, this.modelId, this.icon, this.description, this.timeoutSeconds);
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
  final _imagePicker = ImagePicker();
  
  bool _isLoading = false;
  ModelType _selectedModel = ModelType.agent;
  File? _selectedImage;
  String? _selectedImageUrl;
  
  // Agent API地址
  static const String _apiUrl = 'https://43a018a1-99fd-49f3-a313-a20151d429a3.dev.coze.site/run';

  @override
  void initState() {
    super.initState();
    _requestPermissions();
  }

  Future<void> _requestPermissions() async {
    // Android 13+ 使用新的权限模型
    if (Platform.isAndroid) {
      final status = await Permission.photos.request();
      if (!status.isGranted) {
        debugPrint('相册权限未授予');
      }
    }
  }

  // 发送消息
  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if ((text.isEmpty && _selectedImage == null) || _isLoading) return;

    final messageText = text;
    final imageFile = _selectedImage;
    
    _controller.clear();
    setState(() {
      _selectedImage = null;
      _selectedImageUrl = null;
      
      String displayText = messageText;
      if (imageFile != null) {
        displayText = '[图片] ${messageText.isEmpty ? '' : messageText}';
      }
      
      _messages.add(ChatMessage(
        text: displayText, 
        isUser: true,
        localImage: imageFile,
      ));
      _isLoading = true;
    });
    _scrollToBottom();

    try {
      final response = await _callAgent(messageText, imageFile);
      setState(() {
        _messages.add(ChatMessage(text: response, isUser: false));
      });
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          text: '请求失败: $e\n\n请检查网络连接或重试',
          isUser: false,
          isError: true,
        ));
      });
    } finally {
      setState(() => _isLoading = false);
      _scrollToBottom();
    }
  }

  // 调用Agent
  Future<String> _callAgent(String message, File? imageFile) async {
    final uri = Uri.parse(_apiUrl);
    
    // 构建请求体 - 包含模型选择
    final body = jsonEncode({
      'type': 'query',
      'session_id': 'app_${DateTime.now().millisecondsSinceEpoch}',
      'message': message,
      'model': _selectedModel.modelId, // 传递选择的模型
    });

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: body,
    ).timeout(Duration(seconds: _selectedModel.timeoutSeconds));

    if (response.statusCode == 200) {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      
      // 解析多种响应格式
      if (data['messages'] != null && data['messages'] is List) {
        final messages = data['messages'] as List;
        for (final msg in messages.reversed) {
          final content = msg['content'];
          if (content != null && content.toString().isNotEmpty && msg['type'] != 'human') {
            return content.toString();
          }
        }
      }
      
      if (data['output'] != null) return data['output'].toString();
      if (data['response'] != null) return data['response'].toString();
      if (data['result'] != null) return data['result'].toString();
      if (data['content'] != null) return data['content'].toString();
      
      return '收到响应: ${jsonEncode(data)}';
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  // 选择图片
  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );
      
      if (image != null) {
        setState(() {
          _selectedImage = File(image.path);
          _selectedImageUrl = null;
        });
      }
    } catch (e) {
      _showSnackBar('选择图片失败: $e');
    }
  }

  // 显示图片选择选项
  void _showImageSourceDialog() {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.camera_alt),
                title: const Text('拍照'),
                onTap: () {
                  Navigator.pop(context);
                  _pickImage(ImageSource.camera);
                },
              ),
              ListTile(
                leading: const Icon(Icons.photo_library),
                title: const Text('从相册选择'),
                onTap: () {
                  Navigator.pop(context);
                  _pickImage(ImageSource.gallery);
                },
              ),
              ListTile(
                leading: const Icon(Icons.link),
                title: const Text('输入图片URL'),
                onTap: () {
                  Navigator.pop(context);
                  _showImageUrlDialog();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  // 输入图片URL
  void _showImageUrlDialog() {
    final urlController = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('输入图片URL'),
        content: TextField(
          controller: urlController,
          decoration: const InputDecoration(
            hintText: 'https://example.com/image.jpg',
            border: OutlineInputBorder(),
          ),
          keyboardType: TextInputType.url,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              final url = urlController.text.trim();
              if (url.isNotEmpty && _isImageUrl(url)) {
                setState(() {
                  _selectedImageUrl = url;
                  _selectedImage = null;
                });
              } else {
                _showSnackBar('请输入有效的图片URL');
              }
              Navigator.pop(context);
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  // 判断是否是图片URL
  bool _isImageUrl(String text) {
    final lower = text.toLowerCase();
    return (lower.contains('.jpg') || 
            lower.contains('.jpeg') || 
            lower.contains('.png') || 
            lower.contains('.gif') || 
            lower.contains('.webp')) &&
           lower.startsWith('http');
  }

  // 从文本中提取图片URL
  List<String> _extractImageUrls(String text) {
    final regex = RegExp(
      r'https?://[^\s<>"{}|\\^`\[\]]+\.(?:jpg|jpeg|png|gif|webp)',
      caseSensitive: false,
    );
    return regex.allMatches(text).map((m) => m.group(0)!).toList();
  }

  // 从文本中提取所有URL
  List<String> _extractAllUrls(String text) {
    final regex = RegExp(
      r'https?://[^\s<>"{}|\\^`\[\]]+',
      caseSensitive: false,
    );
    return regex.allMatches(text).map((m) => m.group(0)!).toList();
  }

  // 显示消息操作菜单
  void _showMessageActions(ChatMessage msg, int index) {
    final imageUrls = _extractImageUrls(msg.text);
    final allUrls = _extractAllUrls(msg.text);
    
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(8),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 复制全文
              ListTile(
                leading: const Icon(Icons.copy),
                title: const Text('复制全文'),
                onTap: () {
                  Clipboard.setData(ClipboardData(text: msg.text));
                  Navigator.pop(context);
                  _showSnackBar('已复制到剪贴板');
                },
              ),
              // 如果有图片，显示下载选项
              if (imageUrls.isNotEmpty)
                ...imageUrls.asMap().entries.map((entry) {
                  final idx = entry.key;
                  final url = entry.value;
                  return ListTile(
                    leading: const Icon(Icons.download),
                    title: Text('下载图片 ${idx + 1}'),
                    onTap: () {
                      Navigator.pop(context);
                      _downloadImage(url);
                    },
                  );
                }),
              // 如果有链接，显示复制链接选项
              if (allUrls.isNotEmpty)
                ...allUrls.asMap().entries.map((entry) {
                  final idx = entry.key;
                  final url = entry.value;
                  return ListTile(
                    leading: const Icon(Icons.link),
                    title: Text('复制链接 ${idx + 1}'),
                    subtitle: Text(url.length > 30 ? '${url.substring(0, 30)}...' : url),
                    onTap: () {
                      Clipboard.setData(ClipboardData(text: url));
                      Navigator.pop(context);
                      _showSnackBar('链接已复制');
                    },
                  );
                }),
              // 分享
              ListTile(
                leading: const Icon(Icons.share),
                title: const Text('分享'),
                onTap: () {
                  Navigator.pop(context);
                  Share.share(msg.text);
                },
              ),
              // 另存为文本文件
              ListTile(
                leading: const Icon(Icons.save_alt),
                title: const Text('保存为文本文件'),
                onTap: () {
                  Navigator.pop(context);
                  _saveAsTextFile(msg.text);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  // 下载图片
  Future<void> _downloadImage(String url) async {
    try {
      _showSnackBar('正在下载图片...');
      
      final response = await http.get(Uri.parse(url));
      
      if (response.statusCode == 200) {
        // 获取保存目录
        final directory = Platform.isAndroid
            ? Directory('/storage/emulated/0/Download')
            : await getApplicationDocumentsDirectory();
        
        final fileName = 'calm_ai_${DateTime.now().millisecondsSinceEpoch}.jpg';
        final file = File('${directory.path}/$fileName');
        
        await file.writeAsBytes(response.bodyBytes);
        
        _showSnackBar('图片已保存到: ${file.path}');
      } else {
        throw Exception('下载失败: HTTP ${response.statusCode}');
      }
    } catch (e) {
      _showSnackBar('下载图片失败: $e');
    }
  }

  // 保存为文本文件
  Future<void> _saveAsTextFile(String content) async {
    try {
      final directory = Platform.isAndroid
          ? Directory('/storage/emulated/0/Download')
          : await getApplicationDocumentsDirectory();
      
      final fileName = 'calm_ai_${DateTime.now().millisecondsSinceEpoch}.txt';
      final file = File('${directory.path}/$fileName');
      
      await file.writeAsString(content);
      
      _showSnackBar('文件已保存到: ${file.path}');
    } catch (e) {
      _showSnackBar('保存文件失败: $e');
    }
  }

  // 打开URL
  Future<void> _launchUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      _showSnackBar('无法打开链接');
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
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('清空对话'),
        content: const Text('确定要清空所有对话记录吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() => _messages.clear());
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('清空'),
          ),
        ],
      ),
    );
  }

  void _showModelSelector() {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '选择模型',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 8),
              ...ModelType.values.map((model) {
                final isSelected = model == _selectedModel;
                return Container(
                  margin: const EdgeInsets.symmetric(vertical: 4),
                  decoration: BoxDecoration(
                    color: isSelected 
                        ? Theme.of(context).colorScheme.primaryContainer
                        : null,
                    borderRadius: BorderRadius.circular(12),
                    border: isSelected
                        ? Border.all(
                            color: Theme.of(context).colorScheme.primary,
                            width: 2,
                          )
                        : null,
                  ),
                  child: ListTile(
                    leading: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: isSelected 
                            ? Theme.of(context).colorScheme.primary
                            : Theme.of(context).colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(
                        model.icon,
                        color: isSelected 
                            ? Theme.of(context).colorScheme.onPrimary
                            : null,
                      ),
                    ),
                    title: Text(
                      model.label,
                      style: TextStyle(
                        fontWeight: isSelected ? FontWeight.bold : null,
                      ),
                    ),
                    subtitle: Text(model.description),
                    trailing: isSelected 
                        ? Icon(Icons.check_circle, 
                            color: Theme.of(context).colorScheme.primary)
                        : null,
                    onTap: () {
                      setState(() => _selectedModel = model);
                      Navigator.pop(context);
                      _showSnackBar('已切换到 ${model.label}');
                    },
                  ),
                );
              }),
            ],
          ),
        ),
      ),
    );
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: GestureDetector(
          onTap: _showModelSelector,
          child: Row(
            mainAxisSize: MainAxisSize.min,
              children: [
              const Text('平静 AI'),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(_selectedModel.icon, size: 14),
                    const SizedBox(width: 4),
                    Text(
                      _selectedModel.label,
                      style: const TextStyle(fontSize: 12),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 4),
              Icon(Icons.expand_more, size: 18),
            ],
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.tune),
            onPressed: _showModelSelector,
            tooltip: '选择模型',
          ),
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
                      return _buildMessageBubble(_messages[index], index);
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
            _buildFeatureItem(Icons.image, '画图、生成图片'),
            _buildFeatureItem(Icons.code, '运行代码、计算'),
            _buildFeatureItem(Icons.search, '搜索网络信息'),
            _buildFeatureItem(Icons.chat, '聊天、问答'),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(_selectedModel.icon, size: 20),
                  const SizedBox(width: 8),
                  Text('当前模型: ${_selectedModel.label}'),
                ],
              ),
            ),
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

  Widget _buildMessageBubble(ChatMessage msg, int index) {
    final imageUrls = _extractImageUrls(msg.text);
    final hasImages = imageUrls.isNotEmpty;
    
    String displayText = msg.text;
    for (final url in imageUrls) {
      displayText = displayText.replaceAll(url, '');
    }
    displayText = displayText.trim();
    
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: GestureDetector(
        onLongPress: () => _showMessageActions(msg, index),
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
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // 本地图片预览
                    if (msg.localImage != null) ...[
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.file(
                          msg.localImage!,
                          width: 200,
                          fit: BoxFit.cover,
                        ),
                      ),
                      const SizedBox(height: 8),
                    ],
                    // 显示文本
                    if (displayText.isNotEmpty)
                      SelectableText(
                        displayText,
                        style: TextStyle(
                          color: msg.isUser
                              ? Theme.of(context).colorScheme.onPrimary
                              : msg.isError
                                  ? Theme.of(context).colorScheme.onErrorContainer
                                  : null,
                        ),
                      ),
                    // 显示网络图片
                    if (hasImages) ...[
                      const SizedBox(height: 8),
                      ...imageUrls.map((url) => Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: GestureDetector(
                          onTap: () => _showImagePreview(url),
                          onLongPress: () => _downloadImage(url),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: CachedNetworkImage(
                              imageUrl: url,
                              maxWidth: 250,
                              fit: BoxFit.cover,
                              placeholder: (context, url) => Container(
                                width: 200,
                                height: 150,
                                color: Theme.of(context).colorScheme.surfaceContainerHigh,
                                child: const Center(
                                  child: CircularProgressIndicator(),
                                ),
                              ),
                              errorWidget: (context, url, error) => Container(
                                width: 200,
                                height: 100,
                                decoration: BoxDecoration(
                                  color: Theme.of(context).colorScheme.errorContainer,
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.broken_image, 
                                      color: Theme.of(context).colorScheme.onErrorContainer),
                                    const SizedBox(height: 4),
                                    TextButton(
                                      onPressed: () => _launchUrl(url),
                                      child: const Text('打开链接'),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ),
                      )),
                    ],
                    // 操作提示
                    if (!msg.isUser && !msg.isError) ...[
                      const SizedBox(height: 8),
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.more_horiz, 
                            size: 14, 
                            color: Theme.of(context).colorScheme.onSurfaceVariant),
                          const SizedBox(width: 4),
                          Text(
                            '长按可复制/下载',
                            style: TextStyle(
                              fontSize: 10,
                              color: Theme.of(context).colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
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
      ),
    );
  }

  void _showImagePreview(String url) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => Scaffold(
          appBar: AppBar(
            actions: [
              IconButton(
                icon: const Icon(Icons.download),
                onPressed: () => _downloadImage(url),
                tooltip: '下载图片',
              ),
              IconButton(
                icon: const Icon(Icons.share),
                onPressed: () => Share.share(url),
                tooltip: '分享图片',
              ),
            ],
          ),
          body: Center(
            child: InteractiveViewer(
              child: CachedNetworkImage(
                imageUrl: url,
                fit: BoxFit.contain,
                placeholder: (context, url) => const CircularProgressIndicator(),
                errorWidget: (context, url, error) => const Icon(Icons.error),
              ),
            ),
          ),
        ),
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
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '思考中...',
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                    ),
                    Text(
                      '模型: ${_selectedModel.label}',
                      style: TextStyle(
                        fontSize: 10,
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
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
      padding: EdgeInsets.fromLTRB(8, 8, 8, MediaQuery.of(context).padding.bottom + 8),
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
      child: Column(
        children: [
          // 图片预览
          if (_selectedImage != null || _selectedImageUrl != null)
            Container(
              height: 80,
              margin: const EdgeInsets.only(bottom: 8),
              child: Stack(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: _selectedImage != null
                        ? Image.file(_selectedImage!, height: 80, fit: BoxFit.cover)
                        : CachedNetworkImage(
                            imageUrl: _selectedImageUrl!,
                            height: 80,
                            fit: BoxFit.cover,
                            placeholder: (context, url) => Container(
                              color: Theme.of(context).colorScheme.surfaceContainerHighest,
                              child: const Center(child: CircularProgressIndicator()),
                            ),
                          ),
                  ),
                  Positioned(
                    top: 4,
                    right: 4,
                    child: GestureDetector(
                      onTap: () {
                        setState(() {
                          _selectedImage = null;
                          _selectedImageUrl = null;
                        });
                      },
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: Colors.black54,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.close, color: Colors.white, size: 16),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              // 添加图片按钮
              IconButton(
                onPressed: _showImageSourceDialog,
                icon: Icon(
                  Icons.add_circle_outline,
                  color: Theme.of(context).colorScheme.primary,
                ),
                tooltip: '添加图片',
              ),
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: TextField(
                    controller: _controller,
                    maxLines: 6,
                    minLines: 1,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendMessage(),
                    decoration: const InputDecoration(
                      hintText: '输入消息... (画图、搜索、代码)',
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
  final File? localImage;
  final String? imageUrl;

  ChatMessage({
    required this.text,
    required this.isUser,
    this.isError = false,
    this.localImage,
    this.imageUrl,
  });
}
