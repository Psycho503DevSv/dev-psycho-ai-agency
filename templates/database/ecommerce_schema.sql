-- ═══════════════════════════════════════════════════════════════════════════
--  PSYCHO AI AGENCY — PLANTILLA DE BASE DE DATOS DE E-COMMERCE (SUPABASE)
-- ═══════════════════════════════════════════════════════════════════════════

-- Habilitar UUID si no está habilitado
create extension if not exists "uuid-ossp";

-- ── 1. Tabla de Perfiles de Usuario ───────────────────────────────────────
create table if not exists public.profiles (
    id uuid references auth.users on delete cascade primary key,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    username text unique,
    full_name text,
    avatar_url text,
    role text default 'customer'::text check (role in ('customer', 'admin'))
);

alter table public.profiles enable row level security;

create policy "Perfiles públicos son visibles para todos." on public.profiles
    for select using (true);

create policy "Usuarios pueden actualizar su propio perfil." on public.profiles
    for update using (auth.uid() = id);

-- ── 2. Tabla de Categorías ────────────────────────────────────────────────
create table if not exists public.categories (
    id uuid default uuid_generate_v4() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    name text not null unique,
    slug text not null unique,
    description text
);

alter table public.categories enable row level security;

create policy "Categorías son visibles por todos." on public.categories
    for select using (true);

create policy "Solo administradores pueden modificar categorías." on public.categories
    for all using (
        exists (
            select 1 from public.profiles
            where public.profiles.id = auth.uid() and public.profiles.role = 'admin'
        )
    );

-- ── 3. Tabla de Productos ─────────────────────────────────────────────────
create table if not exists public.products (
    id uuid default uuid_generate_v4() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    name text not null,
    slug text not null unique,
    description text,
    price numeric(10, 2) not null check (price >= 0),
    image_url text,
    stock integer default 0 check (stock >= 0),
    category_id uuid references public.categories(id) on delete set null,
    is_active boolean default true
);

alter table public.products enable row level security;

create policy "Productos activos son visibles por todos." on public.products
    for select using (is_active = true or exists (
        select 1 from public.profiles
        where public.profiles.id = auth.uid() and public.profiles.role = 'admin'
    ));

create policy "Solo administradores pueden modificar productos." on public.products
    for all using (
        exists (
            select 1 from public.profiles
            where public.profiles.id = auth.uid() and public.profiles.role = 'admin'
        )
    );

-- ── 4. Tabla de Órdenes ───────────────────────────────────────────────────
create table if not exists public.orders (
    id uuid default uuid_generate_v4() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    user_id uuid references public.profiles(id) on delete set null,
    status text default 'pending'::text check (status in ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
    total_amount numeric(10, 2) not null default 0.00 check (total_amount >= 0),
    shipping_address text
);

alter table public.orders enable row level security;

create policy "Usuarios pueden ver sus propias órdenes." on public.orders
    for select using (auth.uid() = user_id or exists (
        select 1 from public.profiles
        where public.profiles.id = auth.uid() and public.profiles.role = 'admin'
    ));

create policy "Usuarios pueden crear sus propias órdenes." on public.orders
    for insert with check (auth.uid() = user_id);

create policy "Solo administradores pueden actualizar órdenes." on public.orders
    for update using (
        exists (
            select 1 from public.profiles
            where public.profiles.id = auth.uid() and public.profiles.role = 'admin'
        )
    );

-- ── 5. Tabla de Ítems de Orden ────────────────────────────────────────────
create table if not exists public.order_items (
    id uuid default uuid_generate_v4() primary key,
    order_id uuid references public.orders(id) on delete cascade not null,
    product_id uuid references public.products(id) on delete set null,
    quantity integer not null check (quantity > 0),
    unit_price numeric(10, 2) not null check (unit_price >= 0)
);

alter table public.order_items enable row level security;

create policy "Usuarios pueden ver detalles de sus propias órdenes." on public.order_items
    for select using (
        exists (
            select 1 from public.orders
            where public.orders.id = order_id and (public.orders.user_id = auth.uid() or exists (
                select 1 from public.profiles
                where public.profiles.id = auth.uid() and public.profiles.role = 'admin'
            ))
        )
    );

create policy "Usuarios pueden agregar detalles a sus propias órdenes." on public.order_items
    for insert with check (
        exists (
            select 1 from public.orders
            where public.orders.id = order_id and public.orders.user_id = auth.uid()
        )
    );
