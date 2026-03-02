
import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:audioplayers/audioplayers.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:file_picker/file_picker.dart';

void main() {
  runApp(const BanditApp());
}

class BanditApp extends StatelessWidget {
  const BanditApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Bandit HQ',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFFAA00FF),
        scaffoldBackgroundColor: const Color(0xFF050505),
        textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFAA00FF),
          brightness: Brightness.dark,
          surface: const Color(0xFF121212),
        ),
      ),
      home: const ChatScreen(),
    );
  }
}

class Message {
  final String text;
  final bool isUser;
  final DateTime timestamp;
  final bool isResearch;
  final String? imageBase64;
  final String? thoughts;

  Message({
    required this.text,
    required this.isUser,
    required this.timestamp,
    this.isResearch = false,
    this.imageBase64,
    this.thoughts,
  });
}

class Attachment {
  final String name;
  final Uint8List bytes;
  final String mimeType;

  Attachment({required this.name, required this.bytes, required this.mimeType});
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<Message> _messages = [];
  final List<Attachment> _attachments = [];
  final ScrollController _scrollController = ScrollController();
  final AudioPlayer _audioPlayer = AudioPlayer();
  
  bool _isLoading = false;
  bool _isSpeaking = false;
  bool _researchMode = false;
  bool _searchMode = false;
  bool _imageMode = false;

  final String _apiBase = "https://bandit-849984150802.us-central1.run.app";

  @override
  void initState() {
    super.initState();
    _messages.add(Message(
      text: "Link established. Bandit systems online. How can I assist you today?",
      isUser: false,
      timestamp: DateTime.now(),
    ));
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

  Future<void> _pickFiles() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      allowMultiple: true,
      type: FileType.custom,
      allowedExtensions: ['jpg', 'jpeg', 'png', 'pdf', 'txt'],
      withData: true,
    );

    if (result != null) {
      setState(() {
        for (var file in result.files) {
          if (file.bytes != null) {
            _attachments.add(Attachment(
              name: file.name,
              bytes: file.bytes!,
              mimeType: _getMimeType(file.extension ?? ""),
            ));
          }
        }
      });
    }
  }

  String _getMimeType(String ext) {
    switch (ext.toLowerCase()) {
      case 'jpg':
      case 'jpeg': return 'image/jpeg';
      case 'png': return 'image/png';
      case 'pdf': return 'application/pdf';
      case 'txt': return 'text/plain';
      default: return 'application/octet-stream';
    }
  }

  Future<void> _handleSend() async {
    final text = _controller.text.trim();
    if ((text.isEmpty && _attachments.isEmpty) || _isLoading) return;

    setState(() {
      _messages.add(Message(text: text.isEmpty ? "[Sent ${_attachments.length} files]" : text, isUser: true, timestamp: DateTime.now()));
      _controller.clear();
      _isLoading = true;
    });
    _scrollToBottom();

    try {
      if (_imageMode) {
        // Handle image generation separately
        await _generateImage(text);
      } else {
        // Build multimodal content parts
        List<Map<String, dynamic>> contentParts = [];
        if (text.isNotEmpty) {
          contentParts.add({"type": "text", "text": text});
        }
        
        for (var att in _attachments) {
          String b64 = base64Encode(att.bytes);
          contentParts.add({
            "type": "image_url",
            "image_url": {"url": "data:${att.mimeType};base64,$b64"}
          });
        }

        String endpoint = "/v1/chat/completions";
        Map<String, dynamic> body = {
          "messages": [
            {"role": "user", "content": contentParts.isNotEmpty ? contentParts : text}
          ],
          "thinking_mode": _researchMode ? "thinking" : (_searchMode ? "auto" : "instant")
        };

        // If search mode is explicitly on, we might prefer the /search endpoint if it's simpler
        // but for now, let's keep it robust via chat completions.

        final response = await http.post(
          Uri.parse('$_apiBase$endpoint'),
          headers: {"Content-Type": "application/json"},
          body: jsonEncode(body),
        );

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          final choice = data['choices'][0];
          String replyText = choice['message']['content'] ?? "Neural link error.";
          String? thoughts;

          if (replyText.contains("🧠 **Bandit's Thoughts:**")) {
            final parts = replyText.split("---");
            if (parts.length > 1) {
              thoughts = parts[0].replaceAll("🧠 **Bandit's Thoughts:**", "").trim();
              replyText = parts.sublist(1).join("---").trim();
            }
          }
          
          setState(() {
            _messages.add(Message(
              text: replyText,
              isUser: false,
              timestamp: DateTime.now(),
              thoughts: thoughts,
            ));
            _attachments.clear();
            _isLoading = false;
          });

          if (_isSpeaking) _speak(replyText);
        } else {
          throw Exception("Server returned ${response.statusCode}");
        }
      }
    } catch (e) {
      setState(() {
        _messages.add(Message(
          text: "Communication failure: $e",
          isUser: false,
          timestamp: DateTime.now(),
        ));
        _isLoading = false;
      });
    }
    _scrollToBottom();
  }

  Future<void> _generateImage(String prompt) async {
    final response = await http.post(
      Uri.parse('$_apiBase/generate-image'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"prompt": prompt}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      setState(() {
        _messages.add(Message(
          text: "Generated: ${data['revised_prompt'] ?? prompt}",
          isUser: false,
          timestamp: DateTime.now(),
          imageBase64: data['image'],
        ));
        _isLoading = false;
        _attachments.clear();
      });
    } else {
      throw Exception("Image generation failed");
    }
  }

  Future<void> _speak(String text) async {
    try {
      final response = await http.post(
        Uri.parse('$_apiBase/tts'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"text": text, "voice": "Charon"}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['audio'] != null) {
          final Uint8List audioBytes = base64Decode(data['audio']);
          await _audioPlayer.play(BytesSource(audioBytes));
        }
      }
    } catch (e) {
      debugPrint("TTS error: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'BANDIT HQ',
          style: GoogleFonts.orbitron(
            fontWeight: FontWeight.bold,
            letterSpacing: 2,
            color: const Color(0xFFFF00FF),
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_sweep_outlined),
            onPressed: () => setState(() {
              _messages.clear();
              _messages.add(Message(text: "Terminal cleared.", isUser: false, timestamp: DateTime.now()));
            }),
          ),
          IconButton(
            icon: Icon(_isSpeaking ? Icons.volume_up : Icons.volume_off),
            color: _isSpeaking ? Colors.greenAccent : Colors.grey,
            onPressed: () => setState(() => _isSpeaking = !_isSpeaking),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                return _buildMessageBubble(msg);
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: LinearProgressIndicator(
                backgroundColor: Colors.transparent,
                valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFFF00FF)),
              ),
            ),
          _buildInputArea(),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(Message msg) {
    return Align(
      alignment: msg.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.all(16),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.85,
        ),
        decoration: BoxDecoration(
          color: msg.isUser 
              ? const Color(0xFF2A2A2A) 
              : const Color(0xFF1A1A1A).withOpacity(0.8),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(msg.isUser ? 16 : 0),
            bottomRight: Radius.circular(msg.isUser ? 0 : 16),
          ),
          border: Border.all(
            color: msg.isUser ? Colors.blueAccent.withOpacity(0.3) : const Color(0xFFFF00FF).withOpacity(0.3),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              msg.isUser ? "YOU" : "BANDIT",
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                color: msg.isUser ? Colors.blueAccent : const Color(0xFFFF00FF),
              ),
            ),
            const SizedBox(height: 4),
            if (msg.thoughts != null)
               _buildThoughtsPanel(msg.thoughts!),
            if (msg.imageBase64 != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 8.0),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Image.memory(base64Decode(msg.imageBase64!)),
                ),
              ),
            Text(
              msg.text,
              style: const TextStyle(fontSize: 16, height: 1.4),
            ),
            const SizedBox(height: 8),
            Text(
              DateFormat('HH:mm').format(msg.timestamp),
              style: const TextStyle(fontSize: 10, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildThoughtsPanel(String thoughts) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white.withOpacity(0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.psychology_outlined, size: 14, color: Colors.blueAccent),
              SizedBox(width: 6),
              Text("THINKING PROCESS", style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Colors.blueAccent)),
            ],
          ),
          const SizedBox(height: 6),
          Text(thoughts, style: const TextStyle(fontSize: 12, color: Colors.white70, fontStyle: FontStyle.italic)),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        color: Color(0xFF121212),
        border: Border(top: BorderSide(color: Color(0xFF333333))),
      ),
      child: SafeArea(
        child: Column(
          children: [
            if (_attachments.isNotEmpty) _buildAttachmentPreview(),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildModeChip("IMAGE", _imageMode, () => setState(() { _imageMode = !_imageMode; _searchMode = false; _researchMode = false; }), icon: Icons.image_outlined),
                  const SizedBox(width: 8),
                  _buildModeChip("SEARCH", _searchMode, () => setState(() { _searchMode = !_searchMode; _researchMode = false; _imageMode = false; }), icon: Icons.language),
                  const SizedBox(width: 8),
                  _buildModeChip("RESEARCH", _researchMode, () => setState(() { _researchMode = !_researchMode; _searchMode = false; _imageMode = false; }), icon: Icons.manage_search),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.attach_file, color: Colors.grey),
                  onPressed: _pickFiles,
                ),
                Expanded(
                  child: TextField(
                    controller: _controller,
                    onSubmitted: (_) => _handleSend(),
                    decoration: InputDecoration(
                      hintText: _imageMode ? "Describe image..." : "Enter command...",
                      filled: true,
                      fillColor: const Color(0xFF1E1E1E),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(24), borderSide: BorderSide.none),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                FloatingActionButton(
                  onPressed: _handleSend,
                  backgroundColor: const Color(0xFFFF00FF),
                  mini: true,
                  child: const Icon(Icons.send, color: Colors.black),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAttachmentPreview() {
    return Container(
      height: 60,
      margin: const EdgeInsets.only(bottom: 12),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: _attachments.length,
        itemBuilder: (context, index) {
          final att = _attachments[index];
          return Container(
            margin: const EdgeInsets.only(right: 8),
            padding: const EdgeInsets.symmetric(horizontal: 8),
            decoration: BoxDecoration(color: Colors.white.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
            child: Row(
              children: [
                const Icon(Icons.file_present, size: 16, color: Colors.blueAccent),
                const SizedBox(width: 4),
                Text(att.name, style: const TextStyle(fontSize: 10)),
                IconButton(
                  icon: const Icon(Icons.close, size: 14, color: Colors.redAccent),
                  onPressed: () => setState(() => _attachments.removeAt(index)),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildModeChip(String label, bool isActive, VoidCallback onTap, {IconData? icon}) {
    final activeColor = label == "IMAGE" ? Colors.orangeAccent : (label == "RESEARCH" ? Colors.blueAccent : const Color(0xFFFF00FF));
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isActive ? activeColor.withOpacity(0.2) : Colors.transparent,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: isActive ? activeColor : Colors.grey.withOpacity(0.5)),
        ),
        child: Row(
          children: [
            if (icon != null) ...[Icon(icon, size: 12, color: isActive ? activeColor : Colors.grey), const SizedBox(width: 6)],
            Text(label, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: isActive ? activeColor : Colors.grey)),
          ],
        ),
      ),
    );
  }
}
