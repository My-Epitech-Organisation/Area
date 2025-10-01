import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/applet.dart';

class ApiService {
  static const String baseUrl = 'https://jsonplaceholder.typicode.com'; // Placeholder API for tests
  // Replace with your AREA backend: 'https://your-area-backend.com/api'

  // Fetch the list of applets
  Future<List<Applet>> fetchApplets() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/posts'));

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return data.map((json) => Applet(
          id: json['id'],
          name: 'Applet ${json['id']}',
          description: json['title'],
          triggerService: 'Timer',
          actionService: 'Notification',
          isActive: json['id'] % 2 == 0,
        )).toList();
      } else {
        throw Exception('Failed to load applets');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}