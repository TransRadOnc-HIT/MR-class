import time
import torch
import copy
from mrclass_resnet.utils import save_log

def train_model(model,dataloaders, criterion, optimizer, scheduler, num_epochs,device,dataset_sizes,logger=None):
    
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    epochs_no_improve = 0
    
    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)
        if logger is not None:
            save_log(logger, [
                'Epoch {}/{}'.format(epoch, num_epochs - 1),
                '-' * 10])
        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            
            if phase == 'train':
                
                model.train()  # Set model to training mode
            else:
                model.eval()   # Set model to evaluate mode

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            for step, data in enumerate(dataloaders[phase]):
                
                inputs = data['image']
                labels = data['label']
                inputs = inputs.to(device)
                labels = labels.to(device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward
                # track history if only in train
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                # statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase] 
            
            
            print('{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc))
            
            if logger is not None:
                save_log(logger, ['{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc)])            

            # deep copy the model
            if phase == 'val':
                scheduler.step(epoch_acc *100)
                if epoch_acc > best_acc:
                    best_acc = epoch_acc
                    epochs_no_improve = 0
                    best_model_wts = copy.deepcopy(model.state_dict())
                elif  epoch_acc < best_acc:
                    epochs_no_improve+=1
                    print('No improve in the accuracy in the last {} epoch(s)'.format(
                            epochs_no_improve))
                    if logger is not None:
                        save_log(logger, ['No improve in the accuracy in the last {} epoch(s)'.format(
                                epochs_no_improve)])  
              
            if epochs_no_improve >= 8 and epoch > 5:
                print('Early stopping!' )
                time_elapsed = time.time() - since
                print('Best val Acc: {:4f}'.format(best_acc))
                print('Training complete in {:.0f}m {:.0f}s'.format(
                        time_elapsed // 60, time_elapsed % 60))
                if logger is not None:
                    save_log(logger, [
                        'Early stopping!',
                        'Best val Acc: {:4f}'.format(best_acc),
                        'Training complete in {:.0f}m {:.0f}s'.format(
                            time_elapsed // 60, time_elapsed % 60)])
                model.load_state_dict(best_model_wts)
                return model, best_acc
        

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model, best_acc