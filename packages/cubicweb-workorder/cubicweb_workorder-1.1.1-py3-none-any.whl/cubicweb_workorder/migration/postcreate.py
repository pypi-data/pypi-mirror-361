# postcreate script. You could setup a workflow here for example
from cubicweb import _

# XXX missing correct permissions configuration

# WorkOrder workflow
wwf = add_workflow(_("default workorder workflow"), "WorkOrder")

reserve = wwf.add_state(_("not started"), initial=True)
encours = wwf.add_state(_("in progress"))
attente = wwf.add_state(_("client validation"))
garantie = wwf.add_state(_("warranty"))
recette = wwf.add_state(_("validated"))
annule = wwf.add_state(_("canceled"))

wwf.add_transition(_("cancel"), (reserve,), annule)
wwf.add_transition(_("start"), (reserve,), encours)
wwf.add_transition(_("done"), (encours,), attente)
wwf.add_transition(_("warrant"), (attente,), garantie)
wwf.add_transition(_("validated"), (attente, garantie), recette)


# Order workflow
owf = add_workflow(_("default order workflow"), "Order")

planned = owf.add_state(_("planned"), initial=True)
canceled = owf.add_state(_("canceled"))
sent = owf.add_state(_("sent"))
in_progress = owf.add_state(_("in progress"))
done = owf.add_state(_("done"))
owf.add_transition(_("cancel"), (planned, sent), canceled)
owf.add_transition(_("send"), (planned,), sent)
owf.add_transition(_("receive"), (sent,), in_progress)
owf.add_transition(_("done"), (in_progress,), done)
