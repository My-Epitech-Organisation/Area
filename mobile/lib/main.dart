import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:async';
import 'package:app_links/app_links.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'providers/providers.dart';
import 'pages/splash_page.dart';
import 'pages/login_page.dart';
import 'pages/reset_password_page.dart';
import 'swipe_navigation_page.dart';
import 'utils/debug_helper.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: "assets/.env");
  DebugHelper.printConfiguration();
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();
  late AppLinks _appLinks;
  StreamSubscription? _sub;
  bool _initialLinkHandled = false;

  @override
  void initState() {
    super.initState();
    _appLinks = AppLinks();
    _initDeepLinkListener();
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }

  Future<void> _initDeepLinkListener() async {
    // Handle initial link (app was opened from a link)
    // Only handle it once to avoid issues during hot restart
    try {
      final initialUri = await _appLinks.getInitialLink();
      if (initialUri != null && !_initialLinkHandled) {
        _initialLinkHandled = true;
        // Add delay to ensure navigation is ready
        await Future.delayed(const Duration(milliseconds: 500));
        _handleDeepLink(initialUri);
      }
    } catch (e) {
      debugPrint('Error getting initial link: $e');
    }

    // Handle links while app is running
    _sub = _appLinks.uriLinkStream.listen((Uri? uri) {
      if (uri != null) {
        _handleDeepLink(uri);
      }
    }, onError: (err) {
      debugPrint('Error listening to link stream: $err');
    });
  }

  void _handleDeepLink(Uri uri) {
    debugPrint('Handling deep link: $uri');
    
    // Handle password reset deep link: area://reset-password?token=abc123
    if (uri.scheme == 'area' && uri.host == 'reset-password') {
      final token = uri.queryParameters['token'];
      
      if (token != null && token.isNotEmpty) {
        // Wait for navigator to be ready before pushing
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (navigatorKey.currentState?.mounted ?? false) {
            navigatorKey.currentState?.push(
              MaterialPageRoute(
                builder: (context) => ResetPasswordPage(token: token),
              ),
            );
          }
        });
      } else {
        debugPrint('Reset password link missing token');
      }
    }
    
    // Handle OAuth deep link: myapp://auth/oauth/{provider}/callback?code=xxx&state=yyy
    if (uri.scheme == 'myapp' && uri.host == 'auth') {
      final pathSegments = uri.pathSegments;
      
      if (pathSegments.length >= 3 && 
          pathSegments[0] == 'oauth' && 
          pathSegments[2] == 'callback') {
        
        final provider = pathSegments[1];
        final code = uri.queryParameters['code'];
        final state = uri.queryParameters['state'];
        final error = uri.queryParameters['error'];
        
        String message;
        bool success;
        
        if (error != null) {
          success = false;
          message = uri.queryParameters['error_description'] ?? error;
        } else if (code != null && state != null) {
          success = true;
          message = 'Successfully connected to $provider';
        } else {
          success = false;
          message = 'Invalid OAuth callback parameters';
        }
        
        // Show snackbar notification
        WidgetsBinding.instance.addPostFrameCallback((_) {
          final context = navigatorKey.currentContext;
          if (context != null && context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(message),
                backgroundColor: success ? Colors.green : Colors.red,
                duration: const Duration(seconds: 4),
              ),
            );
          }
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => UserProvider()),
        ChangeNotifierProvider(create: (_) => AppletProvider()),
        ChangeNotifierProvider(create: (_) => ServiceCatalogProvider()),
      ],
      child: MaterialApp(
        navigatorKey: navigatorKey,
        title: 'AREA Mobile',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
          useMaterial3: true,
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
              elevation: 2,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
          ),
          inputDecorationTheme: InputDecorationTheme(
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            filled: true,
            fillColor: Colors.grey.withValues(alpha: 0.1),
          ),
          cardTheme: const CardThemeData(
            elevation: 4,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(16)),
            ),
          ),
        ),
        home: const SplashPage(),
        routes: {
          '/home': (context) => const SwipeNavigationPage(),
          '/login': (context) => const LoginPage(),
        },
        // Error handling
        builder: (context, widget) {
          ErrorWidget.builder = (FlutterErrorDetails errorDetails) {
            return Material(
              child: Container(
                padding: const EdgeInsets.all(16),
                color: Colors.red.shade50,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.error_outline,
                      color: Colors.red,
                      size: 48,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Oops! Something went wrong',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.red,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      errorDetails.exception.toString(),
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Colors.red),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        // Restart the app
                        runApp(const MyApp());
                      },
                      child: const Text('Restart App'),
                    ),
                  ],
                ),
              ),
            );
          };
          return widget ?? const SizedBox.shrink();
        },
      ),
    );
  }
}
