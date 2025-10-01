import 'package:flutter/material.dart';
import '../models/applet.dart';
import '../services/api_service.dart';

class MyAppletsPage extends StatefulWidget {
  const MyAppletsPage({super.key});

  @override
  State<MyAppletsPage> createState() => _MyAppletsPageState();
}

class _MyAppletsPageState extends State<MyAppletsPage> {
  final ApiService _apiService = ApiService();
  List<Applet> _applets = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchApplets();
  }

  Future<void> _fetchApplets() async {
    try {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
      final applets = await _apiService.fetchApplets();
      setState(() {
        _applets = applets;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'My applets page',
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Semantics(
              header: true,
              child: const Text(
                'My Applets:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: _isLoading
                  ? Semantics(
                      label: 'Loading applets',
                      child: const Center(
                        child: CircularProgressIndicator(),
                      ),
                    )
                  : _errorMessage != null
                      ? Semantics(
                          label: 'Error loading applets',
                          child: Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text('Error: $_errorMessage'),
                                const SizedBox(height: 16),
                                Semantics(
                                  button: true,
                                  label: 'Retry loading applets',
                                  hint: 'Tap to try loading applets again',
                                  child: ElevatedButton(
                                    onPressed: _fetchApplets,
                                    style: ElevatedButton.styleFrom(
                                      minimumSize: const Size(120, 48),
                                    ),
                                    child: const Text('Retry'),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        )
                      : Semantics(
                          label: 'Applets list',
                          hint: '${_applets.length} applets available',
                          child: ListView.builder(
                            itemCount: _applets.length,
                            itemBuilder: (context, index) {
                              final applet = _applets[index];
                              return Semantics(
                                label: '${applet.name} applet',
                                hint: '${applet.isActive ? 'Active' : 'Inactive'} applet from ${applet.triggerService} to ${applet.actionService}. ${applet.description}',
                                button: true,
                                child: Card(
                                  child: ListTile(
                                    title: Text(applet.name),
                                    subtitle: Text('${applet.triggerService} → ${applet.actionService}\n${applet.description}'),
                                    trailing: Semantics(
                                      label: applet.isActive ? 'Applet is active' : 'Applet is inactive',
                                      child: Icon(
                                        applet.isActive ? Icons.check_circle : Icons.cancel,
                                        color: applet.isActive ? Colors.green : Colors.red,
                                      ),
                                    ),
                                    onTap: () {
                                      // Action to edit or view details
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        SnackBar(
                                          content: Text('Applet: ${applet.name}'),
                                          duration: const Duration(seconds: 2),
                                        ),
                                      );
                                    },
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
            ),
          ],
        ),
      ),
    );
  }
}