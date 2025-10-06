import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/applet.dart';
import '../config/api_config.dart';
import 'auth_service.dart';

class AppletService {
  final AuthService _authService = AuthService();

  Future<List<Applet>> fetchApplets() async {
    final token = await _authService.getAuthToken();
    final response = await http.get(
      Uri.parse(ApiConfig.appletsUrl),
      headers: {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      },
    );
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Applet.fromJson(json)).toList();
    }
    throw Exception('Failed to load applets');
  }

  // Ajoute ici les autres méthodes CRUD pour les applets
}
