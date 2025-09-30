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
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Applets'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _fetchApplets,
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text(
              'My Applets:',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _errorMessage != null
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text('Error: $_errorMessage'),
                              ElevatedButton(
                                onPressed: _fetchApplets,
                                child: const Text('Retry'),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          itemCount: _applets.length,
                          itemBuilder: (context, index) {
                            final applet = _applets[index];
                            return Card(
                              child: ListTile(
                                title: Text(applet.name),
                                subtitle: Text('${applet.triggerService} → ${applet.actionService}\n${applet.description}'),
                                trailing: Icon(
                                  applet.isActive ? Icons.check_circle : Icons.cancel,
                                  color: applet.isActive ? Colors.green : Colors.red,
                                ),
                                onTap: () {
                                  // Action pour éditer ou voir détails
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(content: Text('Applet: ${applet.name}')),
                                  );
                                },
                              ),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.pushNamed(context, '/create_applet');
        },
        tooltip: 'Create Applet',
        child: const Icon(Icons.add),
      ),
    );
  }
}