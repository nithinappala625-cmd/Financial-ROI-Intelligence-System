import 'package:flutter/material.dart';

void main() {
  runApp(const FinancialDashboardApp());
}

class FinancialDashboardApp extends StatelessWidget {
  const FinancialDashboardApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Financial ROI Dashboard',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF1E1E2C),
      ),
      home: const DashboardHome(),
    );
  }
}

class DashboardHome extends StatefulWidget {
  const DashboardHome({Key? key}) : super(key: key);

  @override
  _DashboardHomeState createState() => _DashboardHomeState();
}

class _DashboardHomeState extends State<DashboardHome> {
  int _currentIndex = 0;

  final List<Widget> _views = [
    const PlaceholderWidget(title: 'Financial Overview'),
    const PlaceholderWidget(title: 'Project ROI Dashboard'),
    const PlaceholderWidget(title: 'Employee Value Scoring'),
    const PlaceholderWidget(title: 'AI Insights & Predictors'),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Agentic Financial Intelligence'),
        centerTitle: true,
      ),
      body: _views[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Overview',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.attach_money),
            label: 'Project ROI',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.people),
            label: 'Employee EVS',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.lightbulb),
            label: 'AI Insights',
          ),
        ],
      ),
    );
  }
}

class PlaceholderWidget extends StatelessWidget {
  final String title;

  const PlaceholderWidget({Key? key, required this.title}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.widgets_outlined, size: 100, color: Colors.blueAccent),
          const SizedBox(height: 20),
          Text(
            title,
            style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          const Text("Live WebSocket & Kafka Integration Pending"),
        ],
      ),
    );
  }
}
