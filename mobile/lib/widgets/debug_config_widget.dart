import 'package:flutter/material.dart';
import '../config/api_config.dart';
import '../config/app_config.dart';
import '../utils/debug_helper.dart';

class DebugConfigWidget extends StatefulWidget {
  final Widget child;

  const DebugConfigWidget({super.key, required this.child});

  @override
  State<DebugConfigWidget> createState() => _DebugConfigWidgetState();
}

class _DebugConfigWidgetState extends State<DebugConfigWidget> {
  final TextEditingController _urlController = TextEditingController();
  bool _showDebugPanel = false;
  bool _forceAndroidLocalhost = false;

  @override
  void initState() {
    super.initState();
    _urlController.text = ApiConfig.baseUrl;
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  void _showConfigDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('API Debug Configuration'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Current effective URL: ${ApiConfig.baseUrl}'),
            const SizedBox(height: 4),
            Text('Tip: ${ApiConfig.physicalDeviceHint('192.168.x.x')}'),
            const SizedBox(height: 16),
            TextField(
              controller: _urlController,
              decoration: InputDecoration(
                labelText: 'Custom URL',
                hintText:
                    'http://${AppConfig.defaultHost}:${AppConfig.defaultPort}',
                border: const OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                if (Theme.of(context).platform == TargetPlatform.android)
                  Expanded(
                    child: CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Force localhost (Android)'),
                      value: _forceAndroidLocalhost,
                      onChanged: (val) {
                        setState(() {
                          _forceAndroidLocalhost = val ?? false;
                          ApiConfig.forceAndroidLocalhost(
                            _forceAndroidLocalhost,
                          );
                        });
                      },
                    ),
                  ),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      final localhostUrl =
                          'http://${AppConfig.defaultHost}:${AppConfig.defaultPort}';
                      ApiConfig.setBaseUrl(localhostUrl);
                      _urlController.text = ApiConfig.baseUrl;
                      setState(() {});
                      Navigator.pop(context);
                    },
                    child: const Text('Localhost'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      final androidUrl =
                          'http://${AppConfig.androidEmulatorHost}:${AppConfig.defaultPort}';
                      ApiConfig.setBaseUrl(androidUrl);
                      _urlController.text = ApiConfig.baseUrl;
                      setState(() {});
                      Navigator.pop(context);
                    },
                    child: const Text('Android'),
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (_urlController.text.isNotEmpty) {
                ApiConfig.setBaseUrl(_urlController.text);
                setState(() {});
              }
              Navigator.pop(context);
            },
            child: const Text('Apply'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: widget.child,
      floatingActionButton: ApiConfig.isDebug
          ? Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (_showDebugPanel)
                  FloatingActionButton(
                    heroTag: "config",
                    mini: true,
                    onPressed: _showConfigDialog,
                    child: const Icon(Icons.settings),
                  ),
                if (_showDebugPanel) const SizedBox(height: 8),
                if (_showDebugPanel)
                  FloatingActionButton(
                    heroTag: "info",
                    mini: true,
                    onPressed: () {
                      DebugHelper.printConfiguration();
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            'Debug info printed. URL: ${ApiConfig.baseUrl}',
                          ),
                          duration: const Duration(seconds: 3),
                        ),
                      );
                    },
                    child: const Icon(Icons.info),
                  ),
                if (_showDebugPanel) const SizedBox(height: 8),
                FloatingActionButton(
                  heroTag: "debug",
                  onPressed: () {
                    setState(() {
                      _showDebugPanel = !_showDebugPanel;
                    });
                  },
                  child: Icon(_showDebugPanel ? Icons.close : Icons.bug_report),
                ),
              ],
            )
          : null,
    );
  }
}
