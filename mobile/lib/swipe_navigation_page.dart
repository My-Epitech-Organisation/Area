import 'package:flutter/material.dart';
import 'home_page.dart';
import 'pages/create_applet_page.dart';
import 'pages/my_applets_page.dart';
import 'pages/widget_examples_page.dart';

class SwipeNavigationPage extends StatefulWidget {
  const SwipeNavigationPage({super.key});

  @override
  State<SwipeNavigationPage> createState() => _SwipeNavigationPageState();
}

class _SwipeNavigationPageState extends State<SwipeNavigationPage> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<Widget> _pages = [
    const MyHomePage(),
    const CreateAppletPage(),
    const MyAppletsPage(),
    const WidgetExamplesPage(),
  ];

  final List<String> _pageTitles = [
    'Dashboard',
    'Create Applet',
    'My Applets',
    'Learn Widgets',
  ];

  final List<IconData> _pageIcons = [
    Icons.home,
    Icons.add,
    Icons.list,
    Icons.widgets,
  ];

  void _onPageChanged(int index) {
    setState(() {
      _currentPage = index;
    });
  }

  void _navigateToPage(int index) {
    _pageController.animateToPage(
      index,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_pageTitles[_currentPage]),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          // Indicateurs de page (dots)
          Row(
            children: List.generate(
              _pages.length,
              (index) => Container(
                margin: const EdgeInsets.symmetric(horizontal: 2),
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _currentPage == index
                      ? Colors.white
                      : Colors.white.withValues(alpha: 0.5),
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: PageView(
        controller: _pageController,
        onPageChanged: _onPageChanged,
        children: _pages,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentPage,
        onTap: _navigateToPage,
        type: BottomNavigationBarType.fixed,
        items: List.generate(
          _pages.length,
          (index) => BottomNavigationBarItem(
            icon: Icon(_pageIcons[index]),
            label: _pageTitles[index],
          ),
        ),
      ),
    );
  }
}