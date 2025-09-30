import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/applet.dart';

class ApiService {
  static const String baseUrl = 'https://jsonplaceholder.typicode.com'; // Placeholder API for tests
  // Replace with your AREA backend: 'https://your-area-backend.com/api'

  // Fetch the list of applets
  Future<List<Applet>> fetchApplets() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/posts')); // Simule des applets avec posts

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        // Adapt JSONPlaceholder data to our Applet model
        return data.map((json) => Applet(
          id: json['id'],
          name: 'Applet ${json['id']}',
          description: json['title'],
          triggerService: 'Timer', // Mock
          actionService: 'Notification', // Mock
          isActive: json['id'] % 2 == 0, // Mock
        )).toList();
      } else {
        throw Exception('Failed to load applets');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Create a new applet (simulation)
  Future<Applet> createApplet(Applet applet) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/posts'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'title': applet.name,
          'body': applet.description,
          'userId': 1,
        }),
      );

      if (response.statusCode == 201) {
        var data = json.decode(response.body);
        return Applet(
          id: data['id'],
          name: applet.name,
          description: applet.description,
          triggerService: applet.triggerService,
          actionService: applet.actionService,
          isActive: true,
        );
      } else {
        throw Exception('Failed to create applet');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // Delete an applet
  Future<void> deleteApplet(int id) async {
    try {
      final response = await http.delete(Uri.parse('$baseUrl/posts/$id'));

      if (response.statusCode != 200) {
        throw Exception('Failed to delete');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}