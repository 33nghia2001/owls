"""
Support Ticket Views for Owls E-commerce Platform
=================================================
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Avg, Q
from .models import (
    TicketCategory, Ticket, TicketMessage,
    TicketAttachment, CannedResponse, TicketStatusHistory
)
from .serializers import (
    TicketCategorySerializer, TicketListSerializer, TicketDetailSerializer,
    CreateTicketSerializer, UpdateTicketSerializer,
    TicketMessageSerializer, CreateTicketMessageSerializer,
    TicketAttachmentSerializer, CannedResponseSerializer,
    TicketStatusHistorySerializer, TicketSatisfactionSerializer
)


# ===== Customer Views =====

class TicketCategoryListView(APIView):
    """List ticket categories for customers."""
    permission_classes = [AllowAny]

    def get(self, request):
        categories = TicketCategory.objects.filter(is_active=True).order_by('order')
        serializer = TicketCategorySerializer(categories, many=True)
        return Response(serializer.data)


class MyTicketsView(APIView):
    """List and create tickets for authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = Ticket.objects.filter(
            customer=request.user
        ).select_related('category').order_by('-created_at')

        # Filter by status
        ticket_status = request.query_params.get('status')
        if ticket_status:
            tickets = tickets.filter(status=ticket_status)

        serializer = TicketListSerializer(tickets, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateTicketSerializer(data=request.data)
        if serializer.is_valid():
            ticket = serializer.save(
                customer=request.user,
                customer_email=request.user.email,
                customer_name=request.user.get_full_name() or request.user.email
            )

            # Create initial message from description
            TicketMessage.objects.create(
                ticket=ticket,
                message_type=TicketMessage.MessageType.CUSTOMER,
                sender=request.user,
                sender_name=ticket.customer_name,
                content=ticket.description
            )

            # Auto-assign if category has default assignee
            if ticket.category and ticket.category.default_assignee:
                ticket.assigned_to = ticket.category.default_assignee
                ticket.save()

            return Response(
                TicketDetailSerializer(ticket).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTicketDetailView(APIView):
    """View and interact with a specific ticket."""
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_number):
        ticket = get_object_or_404(
            Ticket.objects.select_related('category').prefetch_related('messages', 'attachments'),
            ticket_number=ticket_number,
            customer=request.user
        )

        # Filter out internal notes for customer
        serializer = TicketDetailSerializer(ticket)
        data = serializer.data
        data['messages'] = [m for m in data['messages'] if not m['is_internal']]

        return Response(data)


class AddTicketMessageView(APIView):
    """Add a message to a ticket."""
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_number):
        ticket = get_object_or_404(
            Ticket,
            ticket_number=ticket_number,
            customer=request.user
        )

        if ticket.status == Ticket.Status.CLOSED:
            return Response(
                {'detail': 'Cannot add message to closed ticket.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CreateTicketMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(
                ticket=ticket,
                message_type=TicketMessage.MessageType.CUSTOMER,
                sender=request.user,
                sender_name=request.user.get_full_name() or request.user.email,
                is_internal=False  # Customers can't create internal notes
            )

            # Update ticket status if it was waiting on customer
            if ticket.status == Ticket.Status.WAITING_CUSTOMER:
                ticket.status = Ticket.Status.IN_PROGRESS
                ticket.save()

            return Response(
                TicketMessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RateTicketView(APIView):
    """Rate a resolved ticket."""
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_number):
        ticket = get_object_or_404(
            Ticket,
            ticket_number=ticket_number,
            customer=request.user
        )

        if ticket.status not in [Ticket.Status.RESOLVED, Ticket.Status.CLOSED]:
            return Response(
                {'detail': 'Can only rate resolved or closed tickets.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if ticket.satisfaction_rating:
            return Response(
                {'detail': 'Ticket has already been rated.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TicketSatisfactionSerializer(data=request.data)
        if serializer.is_valid():
            ticket.satisfaction_rating = serializer.validated_data['rating']
            ticket.satisfaction_feedback = serializer.validated_data.get('feedback', '')
            ticket.save()

            return Response({'detail': 'Thank you for your feedback!'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===== Agent/Admin Views =====

class AllTicketsView(APIView):
    """List all tickets for agents."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        tickets = Ticket.objects.all().select_related('category', 'assigned_to', 'customer')

        # Filter by status
        ticket_status = request.query_params.get('status')
        if ticket_status:
            tickets = tickets.filter(status=ticket_status)

        # Filter by priority
        priority = request.query_params.get('priority')
        if priority:
            tickets = tickets.filter(priority=priority)

        # Filter by assigned_to
        assigned_to = request.query_params.get('assigned_to')
        if assigned_to:
            if assigned_to == 'me':
                tickets = tickets.filter(assigned_to=request.user)
            elif assigned_to == 'unassigned':
                tickets = tickets.filter(assigned_to__isnull=True)
            else:
                tickets = tickets.filter(assigned_to_id=assigned_to)

        # Filter by category
        category = request.query_params.get('category')
        if category:
            tickets = tickets.filter(category_id=category)

        # Pagination
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))
        start = (page - 1) * per_page
        end = start + per_page

        total_count = tickets.count()
        tickets = tickets.order_by('-created_at')[start:end]

        serializer = TicketListSerializer(tickets, many=True)
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'per_page': per_page
        })


class AdminTicketDetailView(APIView):
    """View and manage a specific ticket (agent)."""
    permission_classes = [IsAdminUser]

    def get(self, request, ticket_number):
        ticket = get_object_or_404(
            Ticket.objects.select_related('category', 'assigned_to').prefetch_related('messages', 'attachments'),
            ticket_number=ticket_number
        )
        serializer = TicketDetailSerializer(ticket)
        return Response(serializer.data)

    def patch(self, request, ticket_number):
        ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
        old_status = ticket.status

        serializer = UpdateTicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            ticket = serializer.save()

            # Track status change
            if 'status' in request.data and old_status != ticket.status:
                TicketStatusHistory.objects.create(
                    ticket=ticket,
                    old_status=old_status,
                    new_status=ticket.status,
                    changed_by=request.user,
                    notes=request.data.get('status_notes', '')
                )

                # Update timestamps
                if ticket.status == Ticket.Status.RESOLVED and not ticket.resolved_at:
                    ticket.resolved_at = timezone.now()
                    ticket.save()
                elif ticket.status == Ticket.Status.CLOSED and not ticket.closed_at:
                    ticket.closed_at = timezone.now()
                    ticket.save()

            return Response(TicketDetailSerializer(ticket).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgentReplyView(APIView):
    """Agent replies to a ticket."""
    permission_classes = [IsAdminUser]

    def post(self, request, ticket_number):
        ticket = get_object_or_404(Ticket, ticket_number=ticket_number)

        serializer = CreateTicketMessageSerializer(data=request.data)
        if serializer.is_valid():
            is_internal = serializer.validated_data.get('is_internal', False)

            message = serializer.save(
                ticket=ticket,
                message_type=TicketMessage.MessageType.NOTE if is_internal else TicketMessage.MessageType.AGENT,
                sender=request.user,
                sender_name=request.user.get_full_name() or request.user.email
            )

            # Track first response time
            if not ticket.first_response_at and not is_internal:
                ticket.first_response_at = timezone.now()

            # Update status
            if ticket.status == Ticket.Status.OPEN and not is_internal:
                ticket.status = Ticket.Status.WAITING_CUSTOMER
                ticket.save()

            return Response(
                TicketMessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignTicketView(APIView):
    """Assign or reassign a ticket."""
    permission_classes = [IsAdminUser]

    def post(self, request, ticket_number):
        ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
        assignee_id = request.data.get('assigned_to')

        if assignee_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            assignee = get_object_or_404(User, id=assignee_id)
            ticket.assigned_to = assignee
        else:
            # Self-assign
            ticket.assigned_to = request.user

        ticket.save()
        return Response({
            'detail': f'Ticket assigned to {ticket.assigned_to.email}',
            'assigned_to': str(ticket.assigned_to.id)
        })


class TicketStatusHistoryView(APIView):
    """View ticket status history."""
    permission_classes = [IsAdminUser]

    def get(self, request, ticket_number):
        ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
        history = ticket.status_history.select_related('changed_by').order_by('-created_at')
        serializer = TicketStatusHistorySerializer(history, many=True)
        return Response(serializer.data)


class CannedResponseListView(APIView):
    """List canned responses for agents."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        responses = CannedResponse.objects.filter(is_active=True)

        category = request.query_params.get('category')
        if category:
            responses = responses.filter(category_id=category)

        responses = responses.order_by('-use_count')
        serializer = CannedResponseSerializer(responses, many=True)
        return Response(serializer.data)


class TicketStatsView(APIView):
    """Get ticket statistics."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Status counts
        status_counts = Ticket.objects.values('status').annotate(count=Count('id'))

        # Priority counts for open tickets
        priority_counts = Ticket.objects.exclude(
            status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]
        ).values('priority').annotate(count=Count('id'))

        # Average satisfaction rating
        avg_rating = Ticket.objects.filter(
            satisfaction_rating__isnull=False
        ).aggregate(avg=Avg('satisfaction_rating'))

        # SLA metrics
        total_tickets = Ticket.objects.count()
        breached_tickets = Ticket.objects.filter(sla_breached=True).count()

        return Response({
            'status_counts': {s['status']: s['count'] for s in status_counts},
            'priority_counts': {p['priority']: p['count'] for p in priority_counts},
            'average_satisfaction': avg_rating['avg'],
            'sla_breach_rate': (breached_tickets / total_tickets * 100) if total_tickets else 0,
            'total_tickets': total_tickets
        })
