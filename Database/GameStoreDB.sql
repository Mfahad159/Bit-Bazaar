USE GAMESTOREDB; 
--------------------------------------------------------------------------
--                            USERS TABLE
--------------------------------------------------------------------------

CREATE TABLE Users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(50) NOT NULL UNIQUE,
    email NVARCHAR(100) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL, -- Store hashed passwords, length depends on hash algorithm
    role VARCHAR(20) NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'admin')),
    created_at DATETIME2 NOT NULL DEFAULT GETDATE() -- GETDATE() gets the current date and time
);
GO
--------------------------------------------------------------------------
--                            GAMES TABLE
--------------------------------------------------------------------------
CREATE TABLE Games (
    game_id INT PRIMARY KEY IDENTITY(1,1),
    title NVARCHAR(150) NOT NULL,
    description NVARCHAR(MAX) NULL, -- MAX allows for very long text, NULL allows it to be empty
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0), -- Price must be a positive value
    genre NVARCHAR(50) NULL,
    platform NVARCHAR(50) NULL,
    release_date DATE NULL, -- Storing only the date part
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    image_url NVARCHAR(2048) NULL, -- For longer URLs
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
GO

-- Optional: Create a trigger to automatically update 'updated_at' timestamp on any update to a row.
-- This is good practice for tables that change often.
CREATE TRIGGER trg_Games_Update_UpdatedAt
ON Games
AFTER UPDATE
AS
BEGIN
    -- Ensure multiple rows can be handled if an update affects them
    IF UPDATE(updated_at) -- Avoid recursive trigger calls if updated_at was explicitly set
        RETURN;

    UPDATE Games
    SET updated_at = GETDATE()
    FROM Games g
    INNER JOIN inserted i ON g.game_id = i.game_id;
END;
GO



--------------------------------------------------------------------------
--                            ORDERS TABLE
--------------------------------------------------------------------------

CREATE TABLE Orders (
    order_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    order_date DATETIME2 NOT NULL DEFAULT GETDATE(),
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (total_amount >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Awaiting Payment', 'Processing', 'Shipped', 'Delivered', 'Cancelled')),
    shipping_address NVARCHAR(500) NULL, -- A single field for simplified address input
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_Orders_Users FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
GO

-- Optional: Trigger to update 'updated_at' on the Orders table
CREATE TRIGGER trg_Orders_Update_UpdatedAt
ON Orders
AFTER UPDATE
AS
BEGIN
    IF UPDATE(updated_at)
        RETURN;

    UPDATE Orders
    SET updated_at = GETDATE()
    FROM Orders o
    INNER JOIN inserted i ON o.order_id = i.order_id;
END;
GO


--------------------------------------------------------------------------
--                            ORDERITEMS TABLE
--------------------------------------------------------------------------
CREATE TABLE OrderItems (
    order_item_id INT PRIMARY KEY IDENTITY(1,1),
    order_id INT NOT NULL,
    game_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0), -- Must order at least 1
    price_at_purchase DECIMAL(10, 2) NOT NULL CHECK (price_at_purchase >= 0), -- Price of the game when the order was placed

    CONSTRAINT FK_OrderItems_Orders FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    -- ON DELETE CASCADE means if an order is deleted, its corresponding order items are also deleted.
    -- This is often desired; if the main order record is gone, its line items usually should be too.

    CONSTRAINT FK_OrderItems_Games FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE NO ACTION,
    -- ON DELETE NO ACTION (or ON DELETE RESTRICT) means if someone tries to delete a game from the Games table
    -- that is part of an existing order item, the deletion will be blocked. This prevents orphaning order item records.
    -- We might want to set it to SET NULL if a game being removed from sale should still show in old orders but as "unavailable".
    -- For now, NO ACTION is a safe default to prevent accidental data loss for historical orders.

    CONSTRAINT UQ_OrderItems_Order_Game UNIQUE (order_id, game_id)
    -- This UNIQUE constraint ensures that you can't add the exact same game_id to the same order_id more than once
    -- as a separate row. If a user wants more of the same game in an order, they should update the quantity of the existing item.
);
GO



--------------------------------------------------------------------------
--                            PAYMENTS TABLE
-------------------------------------------------------------------------

CREATE TABLE Payments (
    payment_id INT PRIMARY KEY IDENTITY(1,1),
    order_id INT NOT NULL UNIQUE, -- Typically, one order has one primary payment attempt/record.
                                 -- If multiple payment attempts for one order are needed, this UNIQUE constraint would be removed
                                 -- and the primary key might become (order_id, payment_attempt_number) or similar.
                                 -- For simplicity and a "simulated" process, one payment record per order is often sufficient.
    payment_date DATETIME2 NOT NULL DEFAULT GETDATE(),
    payment_method VARCHAR(50) NOT NULL DEFAULT 'Simulated', -- e.g., 'SimulatedCard', 'SimulatedPayPal'
    amount_paid DECIMAL(12, 2) NOT NULL CHECK (amount_paid >= 0),
    transaction_id NVARCHAR(100) NULL, -- A mock transaction ID from the simulated payment processor
    payment_status VARCHAR(50) NOT NULL DEFAULT 'Pending' CHECK (payment_status IN ('Pending', 'Success', 'Failed', 'Refunded')),

    CONSTRAINT FK_Payments_Orders FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE
    -- If an order is deleted, its payment record should also be deleted.
);
GO

ALTER TABLE Games
ADD CONSTRAINT UQ_Games_Title UNIQUE (title);
GO
--     -----------================Testing ==============--------

USE GameStoreDB; -- Ensure you are in the correct database context

SELECT * FROM Users;



USE GameStoreDB; -- Ensure you are in the correct database context
SELECT * FROM Games;
    ALTER TABLE Orders
    ADD total_price DECIMAL(10, 2) NOT NULL DEFAULT 0;
USE GameStoreDB; -- Ensure you are in the correct database context
SELECT * FROM Orders;
    ALTER TABLE OrderItems
    ADD price DECIMAL(10, 2) NOT NULL









	ALTER TABLE Games
ALTER COLUMN image_url VARCHAR(MAX);


-- dummy data 

INSERT INTO Games (title, description, price, genre, platform, release_date, stock_quantity, image_url)
VALUES 
('Elder Scrolls V: Skyrim', 'Epic open-world RPG set in the world of Tamriel.', 39.99, 'RPG', 'PC', '2011-11-11', 25, 'data:image/jpeg;base64,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')
,
('God of War', 'Action-adventure game based on Norse mythology.', 49.99, 'Action', 'PlayStation', '2018-04-20', 15, 'https://example.com/godofwar.jpg'),

('Minecraft', 'Sandbox game about placing blocks and going on adventures.', 26.95, 'Sandbox', 'Multi-platform', '2011-11-18', 100, 'https://example.com/minecraft.jpg'),

('Call of Duty: Modern Warfare', 'First-person shooter with modern combat.', 59.99, 'Shooter', 'PC', '2019-10-25', 10, 'https://example.com/codmw.jpg'),

('Among Us', 'Multiplayer party game of teamwork and betrayal.', 4.99, 'Party', 'PC', '2018-06-15', 75, 'https://example.com/amongus.jpg'),

('FIFA 22', 'Realistic football simulation game.', 29.99, 'Sports', 'Multi-platform', '2021-10-01', 30, 'https://example.com/fifa22.jpg'),

('Cyberpunk 2077', 'Open-world sci-fi RPG.', 59.99, 'RPG', 'PC', '2020-12-10', 12, 'https://example.com/cyberpunk.jpg'),

('Stardew Valley', 'Farming simulation RPG with pixel graphics.', 14.99, 'Simulation', 'PC', '2016-02-26', 50, 'https://example.com/stardew.jpg'),

('Hollow Knight', 'Action platformer in a beautifully dark world.', 14.99, 'Metroidvania', 'PC', '2017-02-24', 40, 'https://example.com/hollowknight.jpg'),

('Grand Theft Auto V', 'Action-adventure open-world game.', 29.99, 'Action', 'PC', '2013-09-17', 20, 'https://example.com/gtav.jpg'),

('Overwatch', 'Team-based multiplayer shooter.', 39.99, 'Shooter', 'PC', '2016-05-24', 35, 'https://example.com/overwatch.jpg'),

('Red Dead Redemption 2', 'Western-themed open-world epic.', 49.99, 'Adventure', 'PC', '2018-10-26', 18, 'https://example.com/rdr2.jpg'),

('The Witcher 3: Wild Hunt', 'Fantasy RPG with story-rich content.', 29.99, 'RPG', 'PC', '2015-05-19', 28, 'https://example.com/witcher3.jpg'),

('Fortnite', 'Battle Royale game with building mechanics.', 0.00, 'Battle Royale', 'Multi-platform', '2017-07-25', 200, 'https://example.com/fortnite.jpg'),

('League of Legends', 'Multiplayer online battle arena game.', 0.00, 'MOBA', 'PC', '2009-10-27', 300, 'https://example.com/lol.jpg');
