import 'package:flutter/material.dart';
import 'home_page.dart';
import 'pages/create_applet_page.dart';
import 'pages/my_applets_page.dart';
import 'pages/user_page.dart';

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
    const UserPage(),
  ];

  final List<String> _pageTitles = [
    'Dashboard',
    'Create Applet',
    'My Applets',
    'Profile',
  ];

  final List<IconData> _pageIcons = [
    Icons.home,
    Icons.add,
    Icons.list,
    Icons.person,
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
          Semantics(
            label: 'Page indicators',
            hint: 'Shows current page position. ${_currentPage + 1} of ${_pages.length} pages',
            child: Row(
              children: List.generate(
                _pages.length,
                (index) => Semantics(
                  label: 'Page ${index + 1} indicator',
                  hint: _currentPage == index ? 'Current page' : 'Tap to go to ${_pageTitles[index]} page',
                  button: true,
                  child: GestureDetector(
                    onTap: () => _navigateToPage(index),
                    child: Container(
                      margin: const EdgeInsets.symmetric(horizontal: 2),
                      width: 12, // Increased for better touch target
                      height: 12, // Increased for better touch target
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _currentPage == index
                            ? Colors.white
                            : Colors.white.withValues(alpha: 0.5),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Semantics(
        label: 'Main navigation area',
        hint: 'Swipe left or right to navigate between pages, or use bottom navigation buttons',
        child: PageView(
          controller: _pageController,
          onPageChanged: _onPageChanged,
          children: _pages,
        ),
      ),
      bottomNavigationBar: Semantics(
        label: 'Bottom navigation menu',
        hint: 'Use these buttons to navigate between different sections of the app',
        child: BottomNavigationBar(
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
      ),
    );
  }
}