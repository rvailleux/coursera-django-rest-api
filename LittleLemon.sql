-- Active: 1692686224191@@127.0.0.1@3306@LittleLemon
insert into 
  `Restaurant_menu` (
    title, 
    price, 
    inventory
  )
values
  (
    'Menu 1', 
    3.4, 
    2
  );

  insert into 
  `Restaurant_menu` (
    title, 
    price, 
    inventory
  )
values
  (
    'Menu 2', 
    10, 
    3
  );

  insert into 
  `Restaurant_menu` (
    title, 
    price, 
    inventory
  )
values
  (
    'Menu 3', 
    5, 
    12
  );
  
  insert into 
    `Restaurant_booking` (
      name, 
      no_of_guests, 
      `bookingDate`
    )
  values
    ( 
      'Name 1', 
      2, 
      "2023-10-09"
    );

    insert into 
    `Restaurant_booking` (
      name, 
      no_of_guests, 
      `bookingDate`
    )
  values
    ( 
      'Name 2', 
      4, 
      "2023-10-19"
    );

    insert into 
    `Restaurant_booking` (
      name, 
      no_of_guests, 
      `bookingDate`
    )
  values
    ( 
      'Name 3', 
      12, 
      "2023-10-15"
    );