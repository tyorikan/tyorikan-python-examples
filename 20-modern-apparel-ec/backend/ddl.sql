CREATE TABLE Users (
    UserId STRING(36) NOT NULL,
    Email STRING(MAX),
    PasswordHash STRING(MAX),
    Name STRING(MAX),
    CreatedAt TIMESTAMP
) PRIMARY KEY (UserId);

CREATE TABLE Products (
    ProductId STRING(36) NOT NULL,
    Name STRING(MAX),
    Description STRING(MAX),
    BasePrice INT64,
    CategoryId STRING(MAX),
    CreatedAt TIMESTAMP
) PRIMARY KEY (ProductId);

CREATE TABLE ProductVariants (
    ProductId STRING(36) NOT NULL,
    VariantId STRING(36) NOT NULL,
    Color STRING(MAX),
    Size STRING(MAX),
    StockQuantity INT64
) PRIMARY KEY (ProductId, VariantId),
  INTERLEAVE IN PARENT Products ON DELETE CASCADE;

CREATE TABLE Orders (
    OrderId STRING(36) NOT NULL,
    UserId STRING(36) NOT NULL,
    TotalAmount INT64,
    Status STRING(MAX),
    CreatedAt TIMESTAMP
) PRIMARY KEY (OrderId);

CREATE TABLE OrderItems (
    OrderId STRING(36) NOT NULL,
    ItemId INT64 NOT NULL,
    ProductId STRING(36),
    VariantId STRING(36),
    Quantity INT64,
    UnitPrice INT64
) PRIMARY KEY (OrderId, ItemId),
  INTERLEAVE IN PARENT Orders ON DELETE CASCADE;

CREATE TABLE CartItems (
    UserId STRING(36) NOT NULL,
    ProductId STRING(36) NOT NULL,
    VariantId STRING(36) NOT NULL,
    Quantity INT64 NOT NULL,
    UpdatedAt TIMESTAMP NOT NULL
) PRIMARY KEY (UserId, ProductId, VariantId),
  INTERLEAVE IN PARENT Users ON DELETE CASCADE;
