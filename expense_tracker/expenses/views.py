from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from .models import Expense
from .forms import ExpenseForm, RegisterForm

# --- User Auth ---
def register_view(request):
    if request.user.is_authenticated:
        return redirect('expense_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('expense_list')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

# --- Main Dashboard & Read + Search/Filter + Pagination ---
@login_required
def expense_list(request):
    # Only fetch expenses for current user
    queryset = Expense.objects.filter(user=request.user)

    # Search by Title or Notes
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(notes__icontains=query))

    # Filter by Category
    category_filter = request.GET.get('category')
    if category_filter:
        queryset = queryset.filter(category=category_filter)

    # Calculations on the filtered queryset
    total_spent = queryset.aggregate(Sum('amount'))['amount__sum'] or 0.00

    # Pagination (5 expenses per page)
    paginator = Paginator(queryset, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_spent': total_spent,
        'categories': Expense.CATEGORY_CHOICES,
        'query': query or '',
        'selected_category': category_filter or '',
    }
    return render(request, 'expenses/expense_list.html', context)

# --- Create Expense ---
@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Add New Expense'})

# --- Update Expense ---
@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Edit Expense'})

# --- Delete Expense ---
@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})
# Create your views here.
