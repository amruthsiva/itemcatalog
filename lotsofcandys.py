from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Candyshop, Base, Candy, User

engine = create_engine('sqlite:///toffees.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create fake user
User1 = User(name="siva kumar", email="15PA1A0453@vishnu.edu.in",
             picture='https://bit.ly/2JOTZ8j')
session.add(User1)
session.commit()

# candies in candyman
candyshop1 = Candyshop(user_id=1, name="Candyman")

session.add(candyshop1)
session.commit()

candy2 = Candy(user_id=1, name="Eclairs", description="Birthday Pack",
               price="$200", course="Appetizer", candyshop=candyshop1)

session.add(candy2)
session.commit()


candy1 = Candy(user_id=1, name="Licks", description="Birthday Pack",
               price="$248.99", course="Appetizer", candyshop=candyshop1)

session.add(candy1)
session.commit()

candy2 = Candy(user_id=1, name="Fruitee Fun", description=" Birthday Pack ",
               price="$521.50", course="Appetizer", candyshop=candyshop1)

session.add(candy2)
session.commit()

candy3 = Candy(user_id=1, name="Double Eclairs ", description="Birthday Pack",
               price="$356", course="Appetizer", candyshop=candyshop1)

session.add(candy3)
session.commit()
# candies in nestle
candyshop2 = Candyshop(user_id=1, name="Nestle")

session.add(candyshop2)
session.commit()


candy1 = Candy(user_id=1, name="Kitkat", description="Birthday Pack",
               price="$73.99", course="Appetizer", candyshop=candyshop2)

session.add(candy1)
session.commit()

candy2 = Candy(user_id=1, name="Polo", description="Birthday Pack",
               price="$257", course="Appetizer", candyshop=candyshop2)
session.add(candy2)
session.commit()

candy3 = Candy(user_id=1, name="Milkybar", description="Birthday Pack",
               price="$215", course="Appetizer", candyshop=candyshop2)

session.add(candy3)
session.commit()
# candies in Hershey
candyshop1 = Candyshop(user_id=1, name="Hershey")

session.add(candyshop1)
session.commit()


candy1 = Candy(user_id=1, name="Reese's Peanut Butter Cups",
               description="Birthday Pack",
               price="$84.99", course="Entree", candyshop=candyshop1)

session.add(candy1)
session.commit()

candy2 = Candy(user_id=1, name="Hershey Bar", description="Birthday Pack",
               price="$63.99", course="Entree", candyshop=candyshop1)

session.add(candy2)
session.commit()

candy3 = Candy(user_id=1, name="Krackle", description="Birthday Pack",
               price="$92.95", course="Entree", candyshop=candyshop1)

session.add(candy3)
session.commit()
# candies in mars
candyshop1 = Candyshop(user_id=1, name="Mars")

session.add(candyshop1)
session.commit()


candy1 = Candy(user_id=1, name="Snickers", description="Birthday Pack",
               price="$220.99", course="Entree", candyshop=candyshop1)

session.add(candy1)
session.commit()

candy2 = Candy(user_id=1, name="Milkyway", description="Birthday Pack",
               price="$225.99", course="Entree", candyshop=candyshop1)

session.add(candy2)
session.commit()

candy3 = Candy(user_id=1, name="Twix",
               description="Birthday Pack", price="$40.50",
               course="Entree", candyshop=candyshop1)

session.add(candy3)
session.commit()
print "added all candies!"
