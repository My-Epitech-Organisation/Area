import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:async';
import 'package:app_links/app_links.dart';
import 'providers/providers.dart';
import 'pages/splash_page.dart';
import 'pages/login_page.dart';
import 'pages/reset_password_page.dart';
import 'pages/services_page.dart';
import 'pages/service_details_page.dart';
import 'models/service.dart';
import 'swipe_navigation_page.dart';
import 'utils/debug_helper.dart';
import 'utils/oauth_deep_link_handler.dart';
import 'services/http_client_service.dart';
import 'config/api_config.dart';
import 'config/app_config.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    AppConfig.validateEnvironment();
    AppConfig.debugPrint('Environment validation passed');
  } catch (e) {
    AppConfig.debugPrint('Environment validation failed: $e');
    if (AppConfig.isProduction) {
      rethrow;
    }
  }

  ApiConfig.initialize();

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
  late OAuthDeepLinkHandler _oauthHandler;

  @override
  void initState() {
    super.initState();
    _appLinks = AppLinks();
    _oauthHandler = OAuthDeepLinkHandler();
    _oauthHandler.onOAuthComplete = _handleOAuthComplete;
    _initDeepLinkListener();
    _initOAuthHandler();
  }

  @override
  void dispose() {
    _sub?.cancel();
    _oauthHandler.dispose();
    super.dispose();
  }

  Future<void> _initOAuthHandler() async {
    await _oauthHandler.initialize();
  }

  void _handleOAuthComplete(String provider, bool success, String? message) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final context = navigatorKey.currentContext;
      if (context != null && context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(message ?? 'OAuth completed for $provider'),
            backgroundColor: success ? Colors.green : Colors.red,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    });
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
    _sub = _appLinks.uriLinkStream.listen(
      (Uri? uri) {
        if (uri != null) {
          _handleDeepLink(uri);
        }
      },
      onError: (err) {
        debugPrint('Error listening to link stream: $err');
      },
    );
  }

  void _handleDeepLink(Uri uri) {
    debugPrint('Handling deep link: $uri');

    if (uri.scheme == AppConfig.urlScheme &&
        uri.host == AppConfig.resetPasswordDeepLink) {
      final token = uri.queryParameters['token'];

      if (token != null && token.isNotEmpty) {
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
  }

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => UserProvider()),
        ChangeNotifierProvider(create: (_) => AppletProvider()),
        ChangeNotifierProvider(create: (_) => ServiceCatalogProvider()),
        ChangeNotifierProvider(create: (_) => ConnectedServicesProvider()),
        ChangeNotifierProvider(create: (_) => AutomationStatsProvider()),
      ],
      child: Builder(
        builder: (context) {
          // Set up authentication failure callback
          final httpClient = HttpClientService();
          httpClient.onAuthenticationFailure = () {
            final authProvider = Provider.of<AuthProvider>(
              context,
              listen: false,
            );
            authProvider.logout();
            WidgetsBinding.instance.addPostFrameCallback((_) {
              navigatorKey.currentState?.pushReplacementNamed('/login');
            });
          };

          return MaterialApp(
            navigatorKey: navigatorKey,
            title: '${AppConfig.appName} Mobile',
            theme: ThemeData(
              colorScheme: ColorScheme.fromSeed(
                seedColor: Colors.blue,
                brightness: Brightness.light,
              ),
              useMaterial3: true,
              fontFamily: 'Roboto',
              elevatedButtonTheme: ElevatedButtonThemeData(
                style: ElevatedButton.styleFrom(
                  elevation: 2,
                  shadowColor: Colors.black.withValues(alpha: 0.2),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
              inputDecorationTheme: InputDecorationTheme(
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Colors.grey.withValues(alpha: 0.1),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 16,
                ),
              ),
              cardTheme: const CardThemeData(
                elevation: 4,
                shadowColor: Colors.black12,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.all(Radius.circular(16)),
                ),
              ),
              appBarTheme: const AppBarTheme(
                elevation: 0,
                centerTitle: true,
                backgroundColor: Colors.transparent,
                foregroundColor: Colors.black,
                surfaceTintColor: Colors.transparent,
              ),
              bottomNavigationBarTheme: const BottomNavigationBarThemeData(
                elevation: 8,
                backgroundColor: Colors.white,
                selectedItemColor: Colors.blue,
                unselectedItemColor: Colors.grey,
                showSelectedLabels: true,
                showUnselectedLabels: true,
                type: BottomNavigationBarType.fixed,
              ),
              navigationBarTheme: NavigationBarThemeData(
                elevation: 8,
                backgroundColor: Colors.white,
                surfaceTintColor: Colors.transparent,
                indicatorColor: Colors.blue.withValues(alpha: 0.1),
                labelTextStyle: WidgetStateProperty.all(
                  const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
                ),
              ),
            ),
            home: const SplashPage(),
            routes: {
              '/home': (context) => const SwipeNavigationPage(),
              '/login': (context) => const LoginPage(),
              '/services': (context) => const ServicesPage(),
              '/service-details': (context) => ServiceDetailsPage(
                service: ModalRoute.of(context)!.settings.arguments as Service,
              ),
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
          );
        },
      ),
    );
  }
}
