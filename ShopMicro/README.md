# 📊 Service Endpoints
API Gateway (http://localhost:8000)

GET /health - Health check
POST /api/users/register - Register user
POST /api/users/login - Login
GET /api/users/me - Get current user
GET /api/products - List products
POST /api/orders - Create order
POST /api/payments - Process payment

Direct Service Access (Development Only)

User Service: http://localhost:8001
Product Service: http://localhost:8002
Order Service: http://localhost:8003
Payment Service: http://localhost:8004
Notification Service: http://localhost:8005
Inventory Service: http://localhost:8006

# Management Interfaces

RabbitMQ Management: http://localhost:15672 (admin/admin)
API Documentation: http://localhost:8000/docs
